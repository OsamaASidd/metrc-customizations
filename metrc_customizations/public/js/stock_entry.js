// Source Package: Active Metrc Packages of the row's item.
// Target Package: Available Metrc Tags (a new package is created under it on submit).
frappe.ui.form.on("Stock Entry", {
	setup(frm) {
		frm.set_query("custom_source_package", "items", (doc, cdt, cdn) => {
			const row = locals[cdt][cdn];
			return { filters: { item_code: row.item_code || "__none__", status: "Active", quantity: [">", 0] } };
		});
		frm.set_query("custom_target_package", "items", () => ({ filters: { status: "Available" } }));
	},
});
