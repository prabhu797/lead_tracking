// Copyright (c) 2025, Prabhudev Desai and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lead', {
    refresh: function(frm) {
        console.log(frappe.user.has_role("Admin"));
        if (!frappe.user.has_role("Admin") && frm.doc.status === "Customer") {
            console.log("Hello");
            frm.set_df_property("status", "read_only", 1);
        }
    }
});
