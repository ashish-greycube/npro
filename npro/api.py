from __future__ import unicode_literals
import frappe, json


@frappe.whitelist()
def set_status_value(self, method):
    if self.status in ["Closed", "Converted", "Lost"]:
        self.sales_stage = "Completed"


@frappe.whitelist()
def remove_standard_crm_values():
    frappe.db.delete(
        "Lead Source",
        {
            "name": [
                "not in",
                [
                    "Tele calling referral",
                    "Tele calling",
                    "LinkedIn",
                    "Campaign",
                    "Mass Mailing",
                    "Cold Calling",
                    "Advertisement",
                    "Reference",
                    "Existing Customer",
                ],
            ]
        },
    )
    frappe.db.delete(
        "Opportunity Type", {"name": ["not in", ["Project", "Consulting"]]}
    )
    frappe.db.delete(
        "Sales Stage",
        {
            "name": [
                "not in",
                [
                    "Completed",
                    "Discovery Call",
                    "NPro Candidate Sourcing",
                    "Client Interview",
                    "Client CV Screening",
                    "Candidate Approved",
                    "New",
                    "Negotiation",
                    "Proposal Sent",
                    "Needs Analysis",
                    "Prospecting",
                ],
            ]
        },
    )
    frappe.db.commit()


def on_update_contact(doc, method=None):
    print("*" * 100, "update contact")
    if not doc.department_cf:
        for d in doc.links:
            if d.link_doctype == "Lead":
                doc.department_cf = frappe.db.get_value(
                    "Lead", d.link_name, "department_cf"
                )
                break


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def contact_for_customer_query(doctype, txt, searchfield, start, page_len, filters):
    """returns Contacts linked to Customer of filters.contact"""
    filters["txt"] = "%" + txt + "%"
    return frappe.db.sql(
        """select parent
             from 
                `tabDynamic Link` dl 
             where 
                dl.parenttype = 'Contact' and dl.link_doctype = 'Customer'
                and dl.link_name in (
                    select link_name 
                    from `tabDynamic Link` x 
                    where x.parenttype='Contact' and x.link_doctype = 'Customer'
                    and x.parent = %(contact)s
                )
                and parent like %(txt)s
                and parent <> %(contact)s""",
        filters,
        as_dict=False,
    )
