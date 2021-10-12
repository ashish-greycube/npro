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
                op.customer_name, op.opportunity_owner_cf,
                op.business_module, count(*) opportunity_count
            from 
                tabOpportunity op     
            {where_conditions}
            group by op.customer_name, op.opportunity_owner_cf, op.business_module
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
            "label": _("Organization"),
            "fieldname": "customer_name",
            "width": 200,
        },
        {
            "label": _("Business Modile"),
            "fieldname": "business_module",
            "width": 200,
        },
        {
            "label": _("Opportunity Owner"),
            "fieldname": "opportunity_owner_cf",
            "width": 200,
        },
        {
            "label": _("Count"),
            "fieldname": "opportunity_count",
            "width": 100,
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
