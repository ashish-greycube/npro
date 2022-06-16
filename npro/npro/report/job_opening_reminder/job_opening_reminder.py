# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, today
import pandas


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters):
    filters["today"] = today()
    data = frappe.db.sql(
        """ 
        select 
            name, job_title, opportunity_cf, npro_sourcing_owner_cf, customer_cf, 
            datediff(%(today)s,modified) days_since
        from 
            `tabJob Opening` tjo 
        {where_conditions}
    """.format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
        # debug=True,
    )
    return data


def get_columns(filters):
    return [
        {
            "label": "Job Opening",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Job Opening",
            "width": 145,
        },
        {
            "label": "Job Title",
            "fieldname": "job_title",
            "width": 245,
        },
        {
            "label": "Opportunity",
            "fieldname": "opportunity_cf",
            "fieldtype": "Link",
            "options": "Opportunity",
            "width": 195,
        },
        {
            "label": "Customer",
            "fieldname": "customer_cf",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 235,
        },
        {
            "label": "NPro Sourcing Owner",
            "fieldname": "npro_sourcing_owner_cf",
            "fieldtype": "Link",
            "options": "User",
            "width": 225,
        },
        {
            "label": "Days since Last Activity",
            "fieldname": "days_since",
            "fieldtype": "Int",
            "width": 175,
        },
    ]


def get_conditions(filters):
    conditions = ["tjo.status = 'OPen'"]
    if filters.get("from_date"):
        conditions += ["tjo.creation >= %(from_date)s"]
    if filters.get("to_date"):
        conditions += ["tjo.creation <= %(to_date)s"]

    return conditions and " where " + " and ".join(conditions) or ""
