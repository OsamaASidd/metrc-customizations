// Copyright (c) 2026, alltechvirtual.com and contributors
// For license information, please see license.txt

frappe.ui.form.on("Metrc Tag", {
	refresh(frm) {
		// Only our own facility licenses belong on a Metrc Tag, never a
		// customer's/third party's: offer the rows of every Company's Licenses table.
		frappe
			.xcall("metrc_customizations.metrc_customizations.doctype.metrc_tag.metrc_tag.get_company_licenses")
			.then((opts) => {
				// Keep a value already saved on the tag even if its row was since removed.
				const cur = frm.doc.custom_license;
				if (cur && !opts.some((o) => o.value === cur)) opts.push({ value: cur, label: cur });
				frm.set_df_property("custom_license", "options", [{ value: "", label: "" }, ...opts]);
			});
	},

	tag_code(frm) {
		if (frm.doc.tag_code) {
			frm.set_value("muid", frm.doc.tag_code.slice(-4));
		}
	},
});
