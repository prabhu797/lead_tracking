# Copyright (c) 2025, Prabhudev Desai and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Lead(Document):

    def before_save(doc):
        old_doc = frappe.get_doc("Lead", doc.name) if frappe.db.exists("Lead", doc.name) else None
        
        # Prevent moving back to Cold Calling
        if old_doc and old_doc.status != "Cold Calling" and doc.status == "Cold Calling":
            frappe.throw("Leads cannot be moved back to Cold Calling.")

        # Ensure only Admin or L1 - Team Leader can change Lead status
        if old_doc and old_doc.status != doc.status:
            if not check_current_user_role(["Admin", "L1 - Team Leader"]):
                frappe.throw("Only Admin or L1 - Team Leader can change Lead status.")

        # Ensure L2 - Team Member cannot set substatus to "Completed"
        if doc.substatus == "Completed" and check_current_user_role(["L2 - Team Member"]):
            frappe.throw("L2 - Team Member cannot change substatus to 'Completed'.")

        # Handle Lead Assignment on Status Change
        if old_doc and old_doc.status != doc.status:
            assign_lead_round_robin(doc)

def assign_lead_round_robin(doc):
    """Assigns lead to the correct team based on status change"""
    team_type = get_team_type_for_status(doc.status)
    
    if not team_type:
        return  # No reassignment needed

    teams = frappe.get_all("Team", filters={"team_type": team_type}, fields=["name"])
    if not teams:
        frappe.throw(f"No teams found for {team_type}")

    # Get last assigned team from Lead Assignment Tracker
    tracker = frappe.get_value("Lead Assignment Tracker", {"team_type": team_type}, "last_assigned_team")
    
    # Find the next team in the list (Round Robin)
    next_index = 0
    if tracker and tracker in [t["name"] for t in teams]:
        last_index = [t["name"] for t in teams].index(tracker)
        next_index = (last_index + 1) % len(teams)

    assigned_team = teams[next_index]["name"]
    doc.assigned_team = assigned_team

    # Assign round-robin user (L2 - Team Member) within the team
    assign_user_to_lead(doc, assigned_team, team_type)

    # Update Lead Assignment Tracker
    frappe.db.set_value("Lead Assignment Tracker", {"team_type": team_type}, {
        "last_assigned_team": assigned_team,
        "last_assigned_user": doc.assigned_user
    })

def assign_user_to_lead(doc, assigned_team, team_type):
    """Assigns the lead to an L2 - Team Member in a round-robin manner"""
    team_members = frappe.get_all("User", filters={"role": "L2 - Team Member", "team": assigned_team}, fields=["name"])
    
    if team_members:
        last_assigned_user = frappe.get_value("Lead Assignment Tracker", {"team_type": team_type}, "last_assigned_user")
        user_index = 0  # Default to first member
        
        if last_assigned_user and last_assigned_user in [u["name"] for u in team_members]:
            last_index = [u["name"] for u in team_members].index(last_assigned_user)
            user_index = (last_index + 1) % len(team_members)

        assigned_user = team_members[user_index]["name"]
        doc.assigned_user = assigned_user
    else:
        # Default to Team Leader if no L2 - Team Members
        team_leader = frappe.get_value("Team", assigned_team, "team_leader")
        doc.assigned_user = team_leader if team_leader else None

def get_team_type_for_status(status):
    """Maps lead status to the correct team type"""
    status_team_map = {
        "Cold Calling": "CC Team",
        "Lead": "LR Team",
        "Register": "LR Team",
        "Customer": "Customer Team"
    }
    return status_team_map.get(status)

def check_current_user_role(required_roles):
    """Check if the current user has one of the required roles"""
    current_user = frappe.session.user
    user_roles = frappe.get_roles(current_user)
    return any(role in user_roles for role in required_roles)
