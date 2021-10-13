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
                op.name name, op.customer_name, op.opportunity_amount, op.opportunity_owner_cf,
                op.contact_person, op.business_module, op.transaction_date
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
            "label": _("Business Module"),
            "fieldname": "business_module",
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
            "width": 100,
        },
        {
            "label": "Open Opportunity amount",
            "fieldname": "opportunity_amount",
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "label": _("Opportunity Created on"),
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "width": 120,
        },
    ]


def get_conditions(filters):
    where_clause = []
    where_clause.append("op.opportunity_amount > 0")
    # if filters.get("opportunity_type"):
    #     where_clause.append("op.opportunity_type = %(opportunity_type)s")
    # if filters.get("opportunity_owner"):
    #     where_clause.append("op.opportunity_owner_cf = %(opportunity_owner)s")
    if filters.get("from_date"):
        where_clause.append("op.transaction_date >= %(from_date)s")
    if filters.get("till_date"):
        where_clause.append("op.transaction_date <= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
