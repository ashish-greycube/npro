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
        select * from 
        (
            select 
                op.name name, op.customer_name, op.lost_amount_cf, op.opportunity_owner_cf, op.business_module,
                op.source, op.opportunity_type, op.contact_person, 
                coalesce(pr.lost_reason,cons.lost_reason) lost_reason,
                coalesce(pr.requirement,cons.requirement) requirement,
                coalesce(pr.amount,cons.amount) lost_amount
            from 
                tabOpportunity op     
            left outer join 
            (
                select parent, stage, project_name requirement, lost_reason, amount
                from `tabOpportunity Project Detail CT`
                where stage = 'Lost'
            ) pr on pr.parent = op.name and op.opportunity_type = 'Project'
            left outer join 
            (
                select parent, stage, project_name requirement, lost_reason, amount
                from `tabOpportunity Consulting Detail CT`
                where stage = 'Lost'
            ) cons on cons.parent = op.name and op.opportunity_type = 'Consulting'
            {where_conditions}
        ) t where t.lost_amount is not null        
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
            "width": 130,
        },
        {
            "label": _("Opportunity Type"),
            "fieldname": "opportunity_type",
            "width": 130,
        },
        {
            "label": _("Business Modile"),
            "fieldname": "business_module",
            "width": 160,
        },
        {
            "label": _("Contact Person"),
            "fieldname": "contact_person",
            "width": 150,
        },
        {
            "label": "Opportunity Lost Amount",
            "fieldname": "lost_amount",
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "label": _("Lost Reason"),
            "fieldname": "lost_reason",
            "width": 200,
        },
        {
            "label": _("Requirement"),
            "fieldname": "requirement",
            "width": 150,
        },
    ]


def get_conditions(filters):
    where_clause = []
    where_clause.append("op.lost_amount_cf > 0")
    # if filters.get("opportunity_type"):
    #     where_clause.append("op.opportunity_type = %(opportunity_type)s")
    # if filters.get("opportunity_owner"):
    #     where_clause.append("op.opportunity_owner_cf = %(opportunity_owner)s")
    if filters.get("from_date"):
        where_clause.append("op.transaction_date >= %(from_date)s")
    if filters.get("till_date"):
        where_clause.append("op.transaction_date <= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
