frappe.listview_settings['Lead'] = {
    onload: function(listview) {
        if (frappe.user.has_role("L2 - Team Member")) {
            listview.filter_area.add('Lead', 'assigned_user', '=', frappe.session.user);
            listview.refresh();
        }
    },

    refresh: function(listview) {
        if (frappe.user.has_role("L2 - Team Member")) {
            listview.filter_area.add('Lead', 'assigned_user', '=', frappe.session.user);
            listview.refresh();
        }
    }
};
