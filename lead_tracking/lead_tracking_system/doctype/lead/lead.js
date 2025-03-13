// Copyright (c) 2025, Prabhudev Desai and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Lead', {
//     refresh: function(frm) {
//         console.log(frappe.user.has_role("Admin"));
//         if (!frappe.user.has_role("Admin") && frm.doc.status === "Customer") {
//             console.log("Hello");
//             frm.set_df_property("status", "read_only", 1);
//         }
//     }
// });

// UI-Based Restrictions
frappe.ui.form.on('Lead', {
    refresh: function(frm) {
        console.log(frappe.user_roles);

        // Restrict status field for non-Admin users when lead is "Customer"
        if (!frappe.user_roles.includes("Admin") && frm.doc.status === "Customer") {
            console.log("Restricting Status Change for Non-Admins");
            frm.set_df_property("status", "read_only", 1);
        }

        // Restrict status field for L2 - Team Members (they should not change lead status)
        if (frappe.user_roles.includes("L2 - Team Member")) {
            console.log("L2 - Team Member users cannot change lead status.");
            frm.set_df_property("status", "read_only", 1);
        }

        // Ensure only L1 - Team Leader or Admin can mark substatus as "Completed"
        if (frappe.user_roles.includes("L2 - Team Member")) {
            console.log("L2 - Team Member cannot mark substatus as Completed.");
            frm.set_query("substatus", function() {
                return {
                    filters: [["name", "!=", "Completed"]]
                };
            });
        }
    }
});