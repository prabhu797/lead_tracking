# Copyright (c) 2025, Prabhudev Desai and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Lead(Document):

	def before_save(doc, method):
		if doc.status == "Cold Calling":
			assign_to_team(doc, "CC Team")
		elif doc.status in ["Lead", "Register"]:
			assign_to_team(doc, "LR Team")
		elif doc.status == "Customer":
			assign_to_team(doc, "Customer Team")

def assign_to_team(doc, team_type):
	teams = frappe.get_all("Team", filters={"team_type": team_type}, fields=["name"])
	if teams:
		assigned_team = teams[0]["name"]
		doc.assigned_team = assigned_team