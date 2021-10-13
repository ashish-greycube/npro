# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters):
    data = frappe.db.sql(
        """
            select 
                op.name name, op.customer_name, op.contact_person, op.opportunity_owner_cf,
                op.opportunity_amount, 
                op.transaction_date, DATE(op.contact_date) contact_date,
                op.contact_by, op.to_discuss, op.modified_by, date(op.modified) modified, 
                comm.content latest_comment
            from 
                tabOpportunity op
            left outer join
            (
                select ROW_NUMBER() over (PARTITION BY reference_name order by creation desc) rn,
                reference_name, content from tabComment
                where reference_doctype = 'Opportunity' and comment_type = 'Comment'
            ) comm on comm.reference_name = op.name and rn = 1            
{where_conditions}
    order by DATE(op.contact_date) 
        """.format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        # debug=True,
    )
    return data or []


def get_columns(filters):
    return [
        {
            "label": _("Opportunity"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Opportunity",
            "width": 180,
        },
        {
            "label": _("Organization"),
            "fieldname": "customer_name",
            "width": 200,
        },
        {
            "label": _("Contact Person"),
            "fieldname": "contact_person",
            "width": 100,
        },
        {
            "label": _("Opportunity Owner"),
            "fieldname": "opportunity_owner_cf",
            "width": 200,
        },
        {
            "label": "Open Opportunity amount",
            "fieldname": "opportunity_amount",
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "label": _("Opp created on"),
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Next Contact Date"),
            "fieldname": "contact_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Next Contact By"),
            "fieldname": "contact_by",
            "width": 150,
        },
        {
            "label": _("To Discuss"),
            "fieldname": "to_discuss",
            "width": 200,
        },
        {
            "label": _("Latest Comment"),
            "fieldname": "latest_comment",
            "width": 300,
        },
    ]


def get_conditions(filters):
    where_clause = []
    where_clause.append("DATE(op.contact_date) >= '%s'" % frappe.utils.today())
    if filters.get("from_date"):
        where_clause.append("op.transaction_date >= %(from_date)s")
    if filters.get("till_date"):
        where_clause.append("op.transaction_date <= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
