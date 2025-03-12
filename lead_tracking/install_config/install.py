import frappe

def after_install():
    roles = ["Admin", "L1 - Team Leader", "L2 - Team Member"]

    for role in roles:
        role_doc = frappe.new_doc("Role")
        role_doc.role_name = role
        role_doc.save()