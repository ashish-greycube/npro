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
        select t.* , DATEDIFF(t.close_date, t.transaction_date) days_between
        from 
        (
            select 
                op.name, 
                op.customer_name, op.opportunity_owner_cf, op.contact_person, op.won_amount_cf,
                op.transaction_date, 
                coalesce(pr.stage, cons.stage) stage,
                coalesce(pr.opportunity_close_date, cons.opportunity_close_date) close_date
            from 
                tabOpportunity op     
            left outer join 
            (
                select parent, stage, project_name requirement, opportunity_close_date
                from `tabOpportunity Project Detail CT`
            ) pr on pr.parent = op.name and op.opportunity_type = 'Project'
            left outer join 
            (
                select parent, stage, project_name requirement, opportunity_close_date
                from `tabOpportunity Consulting Detail CT`
            ) cons on cons.parent = op.name and op.opportunity_type = 'Consulting'
            {where_conditions}
        ) t 
        where t.stage = 'Won' and t.close_date is not NULL
        """.format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        debug=True,
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
            "label": _("Opportunity Owner"),
            "fieldname": "opportunity_owner_cf",
            "width": 200,
        },
        {
            "label": _("Contact Person"),
            "fieldname": "contact_person",
            "width": 180,
        },
        {
            "label": "Won opportunity amount",
            "fieldname": "won_amount_cf",
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "label": "Won within Days",
            "fieldname": "days_between",
            "fieldtype": "Int",
            "width": 110,
        },
    ]


def get_conditions(filters):
    where_clause = []
    # where_clause.append("op.status = 'Open'")
    if filters.get("from_date"):
        where_clause.append("op.transaction_date >= %(from_date)s")
    if filters.get("till_date"):
        where_clause.append("op.transaction_date <= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
