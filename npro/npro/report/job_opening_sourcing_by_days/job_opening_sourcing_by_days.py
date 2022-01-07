# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, today


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters):
    filters["today"] = today()
    data = frappe.db.sql(
        """ 
        select 
            name, npro_sourcing_owner_cf, customer_cf, job_title, location_cf, 
            datediff(%(today)s,modified) days_until_selection 
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
            "label": "Owner",
            "fieldname": "npro_sourcing_owner_cf",
            "fieldtype": "Link",
            "options": "User",
            "width": 145,
        },
        {
            "label": "Customer",
            "fieldname": "customer_cf",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 145,
        },
        {
            "label": "Job Title",
            "fieldname": "job_title",
            "fieldtype": "Data",
            "width": 145,
        },
        {
            "label": "Customer Contact",
            "fieldname": "contact_cf",
            "width": 145,
        },
        {
            "label": "Days Untill Selection",
            "fieldname": "days_until_selection",
            "fieldtype": "Int",
            "width": 165,
        },
    ]


def get_conditions(filters):
    conditions = ["tjo.status = 'Open'"]
    if filters.get("from_date"):
        conditions += ["tjo.creation >= %(from_date)s"]
    if filters.get("to_date"):
        conditions += ["tjo.creation <= %(to_date)s"]

    return conditions and " where " + " and ".join(conditions) or ""
