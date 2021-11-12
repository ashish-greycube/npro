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
                case when op.opportunity_from = 'Customer' then 'Existing Customer'
                else op.source end source,
                op.opportunity_amount, op.transaction_date, op.contact_date, op.to_discuss,
                op.modified_by, date(op.modified) modified, 
                COALESCE(pr.stage, cons.stage) sales_stage, 
                COALESCE(pr.requirement, cons.requirement) requirement, 
                COALESCE(pr.amount, cons.amount) amount
            from 
                tabOpportunity op
            left outer join 
            (
                select parent, stage, project_name requirement, amount
                from `tabOpportunity Project Detail CT`
            ) pr on pr.parent = op.name and op.opportunity_type = 'Project'
            left outer join 
            (
                select parent, stage, project_name requirement, amount
                from `tabOpportunity Consulting Detail CT`
            ) cons on cons.parent = op.name and op.opportunity_type = 'Consulting'
            {where_conditions}
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
            "label": _("Source"),
            "fieldname": "source",
            "width": 200,
        },
        {
            "label": _("Opportunity Owner"),
            "fieldname": "opportunity_owner_cf",
            "width": 200,
        },
        {
            "label": _("Sales Stage"),
            "fieldname": "sales_stage",
            "width": 200,
        },
        {
            "label": _("Requirement"),
            "fieldname": "requirement",
            "width": 200,
        },
        {
            "label": _("Opp created on"),
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Contact Person"),
            "fieldname": "contact_person",
            "width": 100,
        },
        {
            "label": "Amount",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 110,
        },
    ]


def get_conditions(filters):
    where_clause = []
    where_clause.append("op.status = 'Open'")
    if filters.get("from_date"):
        where_clause.append("op.transaction_date >= %(from_date)s")
    if filters.get("till_date"):
        where_clause.append("op.transaction_date <= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
