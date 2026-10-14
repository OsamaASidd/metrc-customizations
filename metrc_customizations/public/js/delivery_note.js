// Source Package: Active Metrc Packages of the row's item.
frappe.ui.form.on("Delivery Note", {
	setup(frm) {
		frm.set_query("custom_source_package", "items", (doc, cdt, cdn) => {
			const row = locals[cdt][cdn];
			return { filters: { item_code: row.item_code || "__none__", status: "Active", quantity: [">", 0] } };
		});
	},
});
