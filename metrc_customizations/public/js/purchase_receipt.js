// Licence defaults to the company's Default licence (still editable); Target
// MUID only offers Available tags of that licence. Server-side checks live in
// metrc_customizations/purchase_receipt.py.
frappe.ui.form.on("Purchase Receipt", {
	setup(frm) {
		frm.set_query("custom_license", () => ({ filters: { is_company_license: 1 } }));
		frm.set_query("custom_target_muid", "items", () => ({
			filters: { status: "Available", custom_license: frm.doc.custom_license || "__none__" },
		}));
	},
	onload(frm) {
		if (frm.is_new() && !frm.doc.custom_license) set_default_license(frm);
	},
	company(frm) {
		set_default_license(frm);
	},
	custom_license(frm) {
		const stale = (frm.doc.items || []).filter((r) => r.custom_target_muid);
		if (stale.length) {
			stale.forEach((r) => frappe.model.set_value(r.doctype, r.name, "custom_target_muid", ""));
			frappe.show_alert({ message: __("Licence changed — Target MUIDs cleared."), indicator: "orange" });
		}
	},
});

function set_default_license(frm) {
	if (!frm.doc.company) return;
	frappe
		.xcall("metrc_customizations.purchase_receipt.default_license", { company: frm.doc.company })
		.then((lic) => lic && frm.set_value("custom_license", lic));
}
