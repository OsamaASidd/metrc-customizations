"""Stock Entry <-> Metrc Package.

Source Package: stock leaves that package (Movement Log: Out).
Target Package: an Available Metrc Tag; a new package is created under it
(Movement Log: In) -- also on Material Receipt, which has no source.
"""

import frappe
from frappe import _

from metrc_customizations import packages


def validate(doc, method=None):
	used, seen = {}, set()
	for row in doc.items:
		src, tgt = row.get("custom_source_package"), row.get("custom_target_package")
		if src:
			if not row.s_warehouse:
				frappe.throw(_("Row #{0}: a Source Package needs a Source Warehouse.").format(row.idx))
			packages.validate_source(row, src, row.transfer_qty, used)
		if tgt:
			if not row.t_warehouse:
				frappe.throw(_("Row #{0}: a Target Package needs a Target Warehouse.").format(row.idx))
			packages.validate_target(row, tgt, seen)


def on_submit(doc, method=None):
	for row in doc.items:
		src, tgt = row.get("custom_source_package"), row.get("custom_target_package")
		# Target first: the source's Out log links to the new package.
		if tgt:
			packages.create(doc, row, tgt, row.transfer_qty, row.t_warehouse, against=src)
			packages.stamp_ledger(doc, row, tgt, "in")
		if src:
			packages.consume(doc, row, src, row.transfer_qty, against=tgt)
			packages.stamp_ledger(doc, row, src, "out")


def on_cancel(doc, method=None):
	# Sources first, so their Out logs (which point at the targets) are gone
	# before the target packages are deleted.
	for row in doc.items:
		if row.get("custom_source_package"):
			packages.restore(doc, row, row.custom_source_package)
	for row in doc.items:
		if row.get("custom_target_package"):
			packages.remove(doc, row, row.custom_target_package)
