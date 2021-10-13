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
                op.name name, op.customer_name, op.won_amount_cf, op.opportunity_owner_cf, op.business_module
            from 
                tabOpportunity op     
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
            "label": "Won opportunity amount",
            "fieldname": "won_amount_cf",
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "label": _("Business Module"),
            "fieldname": "business_module",
            "width": 200,
        },
        {
            "label": _("Opportunity Owner"),
            "fieldname": "opportunity_owner_cf",
            "width": 200,
        },
    ]


def get_conditions(filters):
    where_clause = []
    where_clause.append("op.won_amount_cf > 0")
    # if filters.get("opportunity_type"):
    #     where_clause.append("op.opportunity_type = %(opportunity_type)s")
    # if filters.get("opportunity_owner"):
    #     where_clause.append("op.opportunity_owner_cf = %(opportunity_owner)s")
    if filters.get("from_date"):
        where_clause.append("op.transaction_date >= %(from_date)s")
    if filters.get("till_date"):
        where_clause.append("op.transaction_date <= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
