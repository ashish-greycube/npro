from __future__ import unicode_literals
import frappe, json

@frappe.whitelist()
def set_status_value(self,method):
    if self.status in ['Closed', 'Converted', 'Lost']:
        self.sales_stage='Completed'

@frappe.whitelist()
def remove_standard_crm_values():
    frappe.db.delete('Lead Source', {'name': ['not in',["Tele calling referral", "Tele calling", "LinkedIn",
                                    "Campaign", "Mass Mailing", "Cold Calling",
                                    "Advertisement", "Reference", "Existing Customer"]]})
    frappe.db.delete('Opportunity Type', {'name': ['not in',["Project","Consulting"]]})
    frappe.db.delete('Sales Stage', {'name': ['not in',["Completed","Discovery Call","NPro Candidate Sourcing",
                                    "Client Interview","Client CV Screening","Candidate Approved",
                                    "New","Negotiation","Proposal Sent",
                                    "Needs Analysis","Prospecting"]]})
    frappe.db.commit()

