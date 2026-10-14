"""Pull new Metrc tags into Metrc Tag.

Metrc only lists a facility's *available* tags, so this can add tags that are
new in Metrc but cannot see tags that were used or voided there. Existing
Metrc Tag records are never changed.
"""

import frappe
import requests
from frappe.utils import now_datetime
from frappe.utils.password import get_decrypted_password

KINDS = {"package": "Package", "plant": "Plant"}


def _licences():
	"""(licence, user key) for every active Company licence; a licence with no
	key of its own on Metrc Config uses the form's User API key."""
	cfg = frappe.get_single("Metrc Config")
	default_key = cfg.get_password("user_key", raise_exception=False)
	keys = {
		r.license_number: get_decrypted_password(r.doctype, r.name, "user_key", raise_exception=False)
		for r in cfg.licences
	}
	numbers = frappe.get_all(
		"Company License", filters={"parenttype": "Company", "is_active": 1}, pluck="license_number", distinct=True
	)
	return cfg, [(n, keys.get(n) or default_key) for n in numbers]


def sync_tags():
	"""Scheduled every 15 minutes."""
	cfg, licences = _licences()
	base = (cfg.base_url or "").rstrip("/")
	vendor = cfg.get_password("api_key", raise_exception=False)
	if not base or not vendor:
		return {}

	existing = set(frappe.get_all("Metrc Tag", pluck="name"))
	now, new, report = now_datetime(), [], {}
	for licence, user in licences:
		if not user:
			report[licence] = "no user key"
			continue
		for kind, category in KINDS.items():
			try:
				resp = requests.get(
					f"{base}/tags/v2/{kind}/available",
					params={"licenseNumber": licence},
					auth=(vendor, user),
					timeout=120,
				)
			except requests.RequestException as e:
				report[f"{licence} {kind}"] = str(e)[:100]
				continue
			if resp.status_code == 401:
				continue  # e.g. plant tags on a non-cultivation licence
			if resp.status_code != 200:
				report[f"{licence} {kind}"] = f"HTTP {resp.status_code}"
				continue
			data = resp.json()
			rows = data.get("Data", []) if isinstance(data, dict) else data
			added = 0
			for t in rows:
				label = t.get("Label")
				if label and label not in existing:
					existing.add(label)
					new.append((label, label, label[-4:], "Available", category, licence, "Received", now, now, now, now, "Administrator", "Administrator"))
					added += 1
			report[f"{licence} {kind}"] = added

	if new:
		frappe.db.bulk_insert(
			"Metrc Tag",
			[
				"name", "tag_code", "muid", "status", "tag_category", "custom_license", "custom_metrc_status",
				"custom_metrc_last_synced", "last_updated", "creation", "modified", "owner", "modified_by",
			],
			new,
			chunk_size=5000,
		)
		frappe.db.commit()
	return report


@frappe.whitelist()
def sync_tags_now():
	frappe.only_for("System Manager")
	report = sync_tags()
	return {"added": sum(v for v in report.values() if isinstance(v, int)), "report": report}
