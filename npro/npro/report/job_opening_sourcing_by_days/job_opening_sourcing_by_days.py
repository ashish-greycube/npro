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
            tjo.name, npro_sourcing_owner_cf, tjo.customer_contact_cf, tjo.job_title, tjo.location_cf, 
            datediff(tjo.closed_date_cf, tjo.creation) selected_within_days, tja.selected_candidate
        from 
            `tabJob Opening` tjo 
            left outer join (
	            select concat_ws(', ',applicant_name) selected_candidate, job_title 
	            from `tabJob Applicant`
	            where status = 'Accepted'
	            group by job_title
	        ) tja on tja.job_title = tjo.name
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
            "width": 230,
        },
        {
            "label": "Customer Contact",
            "fieldname": "customer_contact_cf",
            "width": 145,
        },
        {
            "label": "Selected Candidate",
            "fieldname": "selected_candidate",
            "width": 180,
        },
        {
            "label": "Selected within Days",
            "fieldname": "selected_within_days",
            "fieldtype": "Data",
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
