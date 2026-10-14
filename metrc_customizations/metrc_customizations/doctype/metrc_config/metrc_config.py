import frappe
from frappe.model.document import Document
from frappe.utils.password import get_decrypted_password


class MetrcConfig(Document):
	pass


@frappe.whitelist()
def test_connection():
	"""Test the configured Base URL + API Key against Metrc.

	Metrc auth is HTTP Basic (vendor/integrator key : user key). This doctype
	holds the vendor key and, optionally, a user key of its own; if the user
	key field here is blank, falls back to the existing Metrc Settings (the
	first active facility), when that doctype is present.

	The test is a single GET /facilities/v2 — read-only, so it is safe to run
	even against the production endpoint (it never writes anything to Metrc).
	"""
	import requests

	cfg = frappe.get_single("Metrc Config")
	base = (cfg.base_url or "").rstrip("/")
	vendor = cfg.get_password("api_key", raise_exception=False)
	if not base or not vendor:
		frappe.throw("Set Base URL and API Key first, then save.")

	user = cfg.get_password("user_key", raise_exception=False) or _existing_user_key()

	try:
		resp = requests.get(f"{base}/facilities/v2", auth=(vendor, user or ""), timeout=30)
	except Exception as e:
		return {"ok": False, "status_code": None, "message": f"Could not reach {base} — {e}"}

	ok = resp.status_code == 200
	facilities = []
	if ok:
		try:
			data = resp.json()
			rows = data.get("Data", data) if isinstance(data, dict) else data
			for f in (rows or []):
				lic = (f.get("License") or {}).get("Number") if isinstance(f.get("License"), dict) else f.get("LicenseNumber")
				if lic:
					facilities.append(lic)
		except Exception:
			pass

	return {
		"ok": ok,
		"status_code": resp.status_code,
		"message": _explain(resp.status_code),
		"facilities": facilities[:25],
		"used_user_key": bool(user),
	}


def _existing_user_key():
	"""First active facility's User API key from Metrc Settings, if present."""
	if not frappe.db.exists("DocType", "Metrc Settings"):
		return None
	try:
		ms = frappe.get_single("Metrc Settings")
	except Exception:
		return None
	for row in (ms.get("facilities") or []):
		if row.get("is_active"):
			key = get_decrypted_password("Metrc Facility", row.name, "user_key", raise_exception=False)
			if key:
				return key
	return None


def _explain(code):
	return {
		200: "Connected — the key authenticated and Metrc returned facilities.",
		401: "401 Unauthorized — the vendor key and the user key don't belong together for this "
		"endpoint. A production vendor key needs a production User API key (the sandbox user "
		"key won't work against api-ca.metrc.com, and vice-versa).",
		403: "403 Forbidden — authenticated, but this key isn't permitted for that action.",
		404: "404 — endpoint not found at this Base URL. Check the URL.",
	}.get(code, f"HTTP {code} — see response.")


# Read-only endpoints the capabilities panel can call live. Keyed so the browser
# can only ask for one of these — never an arbitrary path or method.
# (path, needs licenseNumber, list endpoint)
# List endpoints are queried over the facility's whole history: without a
# lastModified range Metrc v2 returns only records modified in the last day,
# so e.g. a facility with 320 active packages would show 19.
PROBES = {
	"facilities": ("/facilities/v2", False, False),
	"employees": ("/employees/v2", True, False),
	"units": ("/unitsofmeasure/v2/active", False, False),
	"item_categories": ("/items/v2/categories", True, False),
	"location_types": ("/locations/v2/types", True, False),
	"package_types": ("/packages/v2/types", True, False),
	"adjust_reasons": ("/packages/v2/adjust/reasons", True, False),
	"plant_waste_reasons": ("/plants/v2/waste/reasons", True, False),
	"harvest_waste_types": ("/harvests/v2/waste/types", True, False),
	"transfer_types": ("/transfers/v2/types", True, False),
	"labtest_types": ("/labtests/v2/types", True, False),
	"labtest_states": ("/labtests/v2/states", True, False),
	"plant_tags": ("/tags/v2/plant/available", True, False),
	"package_tags": ("/tags/v2/package/available", True, False),
	"locations": ("/locations/v2/active", True, True),
	"strains": ("/strains/v2/active", True, True),
	"items": ("/items/v2/active", True, True),
	"plant_batches": ("/plantbatches/v2/active", True, True),
	"plants_veg": ("/plants/v2/vegetative", True, True),
	"plants_flower": ("/plants/v2/flowering", True, True),
	"harvests": ("/harvests/v2/active", True, True),
	"packages_active": ("/packages/v2/active", True, True),
	"packages_inactive": ("/packages/v2/inactive", True, True),
	"packages_intransit": ("/packages/v2/intransit", True, True),
	"transfers_incoming": ("/transfers/v2/incoming", True, True),
	"transfers_outgoing": ("/transfers/v2/outgoing", True, True),
	"transfers_rejected": ("/transfers/v2/rejected", True, True),
	"transfer_templates": ("/transfers/v2/templates/outgoing", True, True),
	"sales_receipts": ("/sales/v2/receipts/active", True, True),
}


@frappe.whitelist()
def probe_endpoint(key, license=None):
	"""Run one GET from PROBES against Metrc and return status, count and a sample.

	`license` must be one of the Licences rows; that row's user key is used when
	it has one, otherwise the User API key on this form.
	"""
	import time
	from datetime import datetime, timezone

	import requests

	frappe.has_permission("Metrc Config", "read", throw=True)
	if key not in PROBES:
		frappe.throw(f"Unknown endpoint: {key}")
	path, needs_lic, needs_range = PROBES[key]

	cfg = frappe.get_single("Metrc Config")
	base = (cfg.base_url or "").rstrip("/")
	vendor = cfg.get_password("api_key", raise_exception=False)
	user = cfg.get_password("user_key", raise_exception=False) or _existing_user_key()
	if not base or not vendor:
		frappe.throw("Set Base URL and API Key first, then save.")

	row = None
	if license:
		row = next((r for r in cfg.licences if r.license_number == license), None)
		if not row:
			frappe.throw(f"{license} is not in the Licences table.")
		user = get_decrypted_password(row.doctype, row.name, "user_key", raise_exception=False) or user

	params = {}
	if needs_lic:
		params["licenseNumber"] = license or _license(base, vendor, user)
	if needs_range:
		params["lastModifiedStart"] = "2018-01-01T00:00:00Z"  # Metrc CA go-live
		params["lastModifiedEnd"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
		params["pageNumber"], params["pageSize"] = 1, 15

	started = time.time()
	try:
		resp = requests.get(base + path, params=params, auth=(vendor, user or ""), timeout=60)
	except Exception as e:
		return {"ok": False, "status_code": None, "path": path, "message": f"Could not reach Metrc — {e}"}
	ms = int((time.time() - started) * 1000)

	out = {"ok": resp.status_code == 200, "status_code": resp.status_code, "path": path, "ms": ms,
		"license": params.get("licenseNumber"), "count": None, "sample": []}
	if not out["ok"]:
		out["message"] = _explain(resp.status_code)
		if resp.status_code == 401 and license and not (row and row.user_key):
			out["message"] = (f"401 Unauthorized — the User API key on this form has no access to {license}. "
				"Add a user key for this licence in the Licences table (from a Metrc user with access to that facility).")
		out["body"] = resp.text[:500]
		return out
	try:
		data = resp.json()
	except Exception:
		return out
	rows = data.get("Data", data) if isinstance(data, dict) else data
	if isinstance(rows, list):
		out["count"] = data.get("Total", len(rows)) if isinstance(data, dict) else len(rows)
		out["sample"] = rows[:15]
	else:
		out["sample"] = [rows]
	return out


def _license(base, vendor, user):
	"""First facility licence these keys can see (cached for the session)."""
	cached = frappe.cache.get_value("metrc_probe_license")
	if cached:
		return cached
	import requests

	resp = requests.get(f"{base}/facilities/v2", auth=(vendor, user or ""), timeout=30)
	resp.raise_for_status()
	data = resp.json()
	rows = data.get("Data", data) if isinstance(data, dict) else data
	for f in rows or []:
		lic = (f.get("License") or {}).get("Number") if isinstance(f.get("License"), dict) else f.get("LicenseNumber")
		if lic:
			frappe.cache.set_value("metrc_probe_license", lic, expires_in_sec=3600)
			return lic
	frappe.throw("Metrc returned no facilities for these keys.")
