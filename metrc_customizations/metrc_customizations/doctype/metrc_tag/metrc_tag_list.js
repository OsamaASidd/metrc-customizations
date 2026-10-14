// License is a Select with no stored options (see metrc_tag.js); fill the list
// view's License filter from every Company's Licenses table.
frappe.listview_settings["Metrc Tag"] = {
	...(frappe.listview_settings["Metrc Tag"] || {}),
	onload(listview) {
		frappe
			.xcall("metrc_customizations.metrc_customizations.doctype.metrc_tag.metrc_tag.get_company_licenses")
			.then((opts) => {
				const field = listview.page.fields_dict.custom_license;
				if (!field) return;
				field.df.options = ["", ...opts.map((o) => o.value)];
				field.set_options();
			});
	},
	get_indicator(doc) {
		const color = { Received: "blue", Used: doc.current_qty > 0 ? "green" : "gray", Void: "red" }[doc.status];
		return [__(doc.status), color || "gray", `status,=,${doc.status}`];
	},
	add_fields: ["status", "current_qty"],
};
