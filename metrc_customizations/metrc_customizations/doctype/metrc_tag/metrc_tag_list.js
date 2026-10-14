frappe.listview_settings["Metrc Tag"] = {
	...(frappe.listview_settings["Metrc Tag"] || {}),
	get_indicator(doc) {
		const color = { Available: "blue", Used: doc.current_qty > 0 ? "green" : "gray", Voided: "red" }[doc.status];
		return [__(doc.status), color || "gray", `status,=,${doc.status}`];
	},
	add_fields: ["status", "current_qty"],
};
