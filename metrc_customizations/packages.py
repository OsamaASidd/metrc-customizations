"""Metrc Package movements shared by Purchase Receipt, Stock Entry and Delivery Note.

A row can take stock out of a Source Package (an Active Metrc Package of the
row's item) and/or put it into a new package created under a Target tag (an
Available Metrc Tag, which becomes Used). Every movement is written to the
package's Movement Log, and the package is stamped on the Stock Ledger Entries
the row produced. Cancelling the voucher reverses all of it.
"""

import frappe
from frappe import _
from frappe.utils import flt, now_datetime


# ── validation ────────────────────────────────────────────────────────────────


def validate_source(row, package_name, qty, used):
	"""`used` accumulates qty per package across the voucher's rows."""
	pkg = frappe.db.get_value("Metrc Package", package_name, ["item_code", "status", "quantity"], as_dict=True)
	if not pkg:
		frappe.throw(_("Row #{0}: Metrc Package {1} does not exist.").format(row.idx, frappe.bold(package_name)))
	if pkg.item_code != row.item_code:
		frappe.throw(
			_("Row #{0}: Source Package {1} holds {2}, not {3}.").format(
				row.idx, frappe.bold(package_name), pkg.item_code, row.item_code
			)
		)
	if pkg.status != "Active":
		frappe.throw(_("Row #{0}: Source Package {1} is {2}.").format(row.idx, frappe.bold(package_name), pkg.status))
	used[package_name] = used.get(package_name, 0) + flt(qty)
	if used[package_name] > flt(pkg.quantity) + 1e-9:
		frappe.throw(
			_("Row #{0}: Source Package {1} holds {2}, but this document takes {3} from it.").format(
				row.idx, frappe.bold(package_name), flt(pkg.quantity), used[package_name]
			)
		)


def validate_target(row, tag_name, seen, license=None):
	if tag_name in seen:
		frappe.throw(_("Row #{0}: tag {1} is used on more than one row.").format(row.idx, frappe.bold(tag_name)))
	seen.add(tag_name)
	tag = frappe.db.get_value("Metrc Tag", tag_name, ["status", "custom_license"], as_dict=True)
	if not tag:
		frappe.throw(_("Row #{0}: Metrc Tag {1} does not exist.").format(row.idx, frappe.bold(tag_name)))
	if tag.status != "Available":
		frappe.throw(
			_("Row #{0}: tag {1} is {2}; only Available tags can be used.").format(row.idx, frappe.bold(tag_name), tag.status)
		)
	if license and tag.custom_license != license:
		frappe.throw(
			_("Row #{0}: tag {1} belongs to licence {2}, not {3}.").format(
				row.idx, frappe.bold(tag_name), tag.custom_license or "-", license
			)
		)


# ── submit ────────────────────────────────────────────────────────────────────


def _log(pkg, log_type, doc, row, qty, uom, against=None):
	pkg.append(
		"movement_log",
		{
			"posting_date": doc.posting_date,
			"log_type": log_type,
			"voucher_type": doc.doctype,
			"voucher_no": doc.name,
			"voucher_detail_no": row.name,
			"quantity": flt(qty),
			"uom": uom,
			"against_package": against,
		},
	)


def consume(doc, row, package_name, qty, against=None):
	pkg = frappe.get_doc("Metrc Package", package_name)
	pkg.quantity = flt(pkg.quantity) - flt(qty)
	if pkg.quantity <= 0:
		pkg.quantity = 0
		pkg.status = "Inactive"
	_log(pkg, "Out", doc, row, qty, row.stock_uom, against)
	pkg.save(ignore_permissions=True)


def create(doc, row, tag_name, qty, warehouse, license=None, against=None, source_tags=None):
	if frappe.db.exists("Metrc Package", tag_name):
		frappe.throw(_("Row #{0}: a Metrc Package {1} already exists.").format(row.idx, frappe.bold(tag_name)))
	tag = frappe.get_doc("Metrc Tag", tag_name)
	tag.status = "Used"
	tag.current_qty = flt(qty)
	tag.last_transaction_type = doc.doctype
	tag.last_transaction_id = doc.name
	tag.last_updated = now_datetime()
	tag.save(ignore_permissions=True)

	pkg = frappe.get_doc(
		{
			"doctype": "Metrc Package",
			"tag": tag_name,
			"status": "Active",
			"item_code": row.item_code,
			"uom": row.stock_uom,
			"quantity": flt(qty),
			"original_quantity": flt(qty),
			"license": license or tag.custom_license,
			"warehouse": warehouse,
			"project": row.get("project") or doc.get("project"),
			"purchase_receipt": doc.name if doc.doctype == "Purchase Receipt" else None,
			"purchase_receipt_item": row.name if doc.doctype == "Purchase Receipt" else None,
			"source_tags": source_tags,
		}
	)
	_log(pkg, "In", doc, row, qty, row.stock_uom, against)
	pkg.insert(ignore_permissions=True)


def stamp_ledger(doc, row, package_name, direction):
	"""Write the package onto this row's Stock Ledger Entries: direction "in"
	for the receiving leg (actual_qty > 0), "out" for the issuing leg."""
	sign = ">" if direction == "in" else "<"
	frappe.db.sql(
		f"""update `tabStock Ledger Entry` set custom_metrc_package = %s
		where voucher_type = %s and voucher_no = %s and voucher_detail_no = %s
		  and is_cancelled = 0 and actual_qty {sign} 0""",  # nosemgrep
		(package_name, doc.doctype, doc.name, row.name),
	)


# ── cancel ────────────────────────────────────────────────────────────────────


def restore(doc, row, package_name):
	"""Undo consume(): put the quantity back and drop this voucher's Out log."""
	if not frappe.db.exists("Metrc Package", package_name):
		return
	pkg = frappe.get_doc("Metrc Package", package_name)
	mine = [m for m in pkg.movement_log if m.voucher_type == doc.doctype and m.voucher_no == doc.name
		and m.voucher_detail_no == row.name and m.log_type == "Out"]
	if not mine:
		return
	pkg.quantity = flt(pkg.quantity) + sum(flt(m.quantity) for m in mine)
	if pkg.status == "Inactive" and pkg.quantity > 0:
		pkg.status = "Active"
	pkg.movement_log = [m for m in pkg.movement_log if m not in mine]
	pkg.save(ignore_permissions=True)


def remove(doc, row, tag_name):
	"""Undo create(): delete the package and hand the tag back as Available.
	Refused once anything else has moved stock out of the package."""
	if frappe.db.exists("Metrc Package", tag_name):
		pkg = frappe.get_doc("Metrc Package", tag_name)
		others = [m for m in pkg.movement_log if not (m.voucher_type == doc.doctype and m.voucher_no == doc.name)]
		if others:
			frappe.throw(
				_("Row #{0}: Metrc Package {1} has since been used by {2} {3}; cancel that first.").format(
					row.idx, frappe.bold(tag_name), others[-1].voucher_type, others[-1].voucher_no
				)
			)
		# The only remaining links are this voucher's own (now cancelled) ledger
		# entries -- any later use would be in the Movement Log checked above.
		frappe.db.sql(
			"""update `tabStock Ledger Entry` set custom_metrc_package = null
			where voucher_type = %s and voucher_no = %s and custom_metrc_package = %s""",
			(doc.doctype, doc.name, tag_name),
		)
		frappe.delete_doc("Metrc Package", tag_name, ignore_permissions=True, force=True)
	tag = frappe.get_doc("Metrc Tag", tag_name)
	if tag.last_transaction_id == doc.name:
		tag.status = "Available"
		tag.current_qty = 0
		tag.last_updated = now_datetime()
		tag.save(ignore_permissions=True)
