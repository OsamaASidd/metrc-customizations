"""Purchase Receipt <-> Metrc Tag / Metrc Package.

Each item row may name a Target MUID: an Available Metrc Tag of the receipt's
Licence. Submitting the receipt marks that tag Used and creates a Metrc
Package named after it (Movement Log: In); cancelling undoes both.
"""

import frappe
from frappe import _

from metrc_customizations import packages


def get_default_license(company):
	"""The company's Licenses row ticked Default."""
	if not company:
		return None
	return frappe.db.get_value(
		"Company License",
		{"parenttype": "Company", "parent": company, "is_default": 1, "is_active": 1},
		"license_number",
	)


@frappe.whitelist()
def default_license(company):
	frappe.has_permission("Company", "read", company, throw=True)
	return get_default_license(company)


def _tagged_rows(doc):
	return [row for row in doc.items if row.get("custom_target_muid")]


def validate(doc, method=None):
	if not doc.get("custom_license"):
		doc.custom_license = get_default_license(doc.company)
	if doc.is_return:
		return
	seen = set()
	for row in _tagged_rows(doc):
		if not doc.custom_license:
			frappe.throw(_("Set the Licence before choosing Target MUIDs."))
		packages.validate_target(row, row.custom_target_muid, seen, license=doc.custom_license)


def on_submit(doc, method=None):
	if doc.is_return:
		return
	for row in _tagged_rows(doc):
		packages.create(doc, row, row.custom_target_muid, row.stock_qty, row.warehouse,
			license=doc.custom_license, source_tags=row.get("custom_source_tags"))
		packages.stamp_ledger(doc, row, row.custom_target_muid, "in")


def on_cancel(doc, method=None):
	if doc.is_return:
		return
	for row in _tagged_rows(doc):
		packages.remove(doc, row, row.custom_target_muid)


def validate_company_licenses(doc, method=None):
	"""Company: at most one Default licence row."""
	defaults = [r.license_number for r in doc.get("custom_licenses") or [] if r.is_default]
	if len(defaults) > 1:
		frappe.throw(_("Only one licence can be Default; ticked: {0}.").format(", ".join(defaults)))
