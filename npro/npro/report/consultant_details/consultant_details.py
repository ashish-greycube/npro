# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, today


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters):
    filters["today"] = today()
    data = frappe.db.sql(
        """
    select 
        te.name employee, te.date_of_joining , te.employee_name , tja.customer_cf , teo.boarding_status ,
        te.employment_type , te.npro_technical_manager_cf , te.billing_start_date_cf , candidate_onboarding_checklist_completed_cf
    from tabEmployee te 
    inner join `tabJob Applicant` tja on tja.name = te.job_applicant 
    inner join `tabEmployee Onboarding` teo on teo.job_applicant = te.job_applicant 
        {where_conditions}
        """.format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
    )

    return data


def get_columns(filters):
    return [
        {
            "label": _("Candidate Name"),
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 280,
        },
        {
            "label": _("Client"),
            "fieldname": "customer_cf",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200,
        },
        {
            "label": _("Status"),
            "fieldname": "boarding_status",
            "width": 100,
        },
        {
            "label": _("Date Of Joining"),
            "fieldname": "date_of_joining",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Billing Start Date"),
            "fieldname": "billing_start_date_cf",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Employment Type"),
            "fieldname": "employment_type",
            "width": 120,
        },
        {
            "label": _("Candidate Onboarding Checklist Completed"),
            "fieldname": "candidate_onboarding_checklist_completed_cf",
            "width": 100,
        },
        {
            "label": _("NPro Technical Manager"),
            "fieldname": "npro_technical_manager_cf",
            "width": 120,
        },
    ]


def get_conditions(filters):
    where_clause = []

    if filters.get("from_date"):
        where_clause.append(
            "(te.date_of_joining is null or te.date_of_joining >= %(from_date)s)"
        )
    if filters.get("till_date"):
        where_clause.append(
            "(te.date_of_joining is null or te.date_of_joining <= %(till_date)s)"
        )

    return " where " + " and ".join(where_clause) if where_clause else ""
