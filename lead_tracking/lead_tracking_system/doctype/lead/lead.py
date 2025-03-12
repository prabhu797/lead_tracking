# Copyright (c) 2025, Prabhudev Desai and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Lead(Document):

	def before_save(doc, method):
		# Assign Lead based on Status
		if doc.status == "Cold Calling":
			assign_lead_round_robin(doc, "CC Team")
		elif doc.status in ["Lead", "Register"]:
			assign_lead_round_robin(doc, "LR Team")
		elif doc.status == "Customer":
			assign_lead_round_robin(doc, "Customer Team")

def assign_lead_round_robin(doc, team_type):
    # Get all teams of the given type
    teams = frappe.get_all("Team", filters={"team_type": team_type}, fields=["name"])
    if not teams:
        frappe.throw(f"No teams found for {team_type}")

    # Get last assigned team from Lead Assignment Tracker
    tracker = frappe.get_value("Lead Assignment Tracker", {"team_type": team_type}, ["last_assigned_team"])
    
    # Find the next team in the list
    if tracker and tracker in [t["name"] for t in teams]:
        last_index = [t["name"] for t in teams].index(tracker)
        next_index = (last_index + 1) % len(teams)
    else:
        next_index = 0  # Start from first team

    assigned_team = teams[next_index]["name"]
    doc.assigned_team = assigned_team

    # Get all L2s from this team and assign round-robin
    team_members = frappe.get_all("User", filters={"role": "L2", "team": assigned_team}, fields=["name"])
    if team_members:
        last_assigned_user = frappe.get_value("Lead Assignment Tracker", {"team_type": team_type}, "last_assigned_user")
        user_index = 0  # Default to first member
        if last_assigned_user and last_assigned_user in [u["name"] for u in team_members]:
            last_index = [u["name"] for u in team_members].index(last_assigned_user)
            user_index = (last_index + 1) % len(team_members)

        assigned_user = team_members[user_index]["name"]
        doc.assigned_user = assigned_user
    else:
        # Default to Team Leader if no L2s
        team_leader = frappe.get_value("Team", assigned_team, "team_leader")
        doc.assigned_user = team_leader if team_leader else None

    # Update tracker for next assignment
    frappe.db.set_value("Lead Assignment Tracker", {"team_type": team_type}, {
        "last_assigned_team": assigned_team,
        "last_assigned_user": doc.assigned_user
    })
