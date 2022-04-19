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
    teo.job_applicant , teo.employee_name , teo.date_of_joining , tja.customer_cf , 
    tjo.opportunity_technology_cf , tjo.customer_contact_cf , tjo.location_cf , tjo.npro_sourcing_owner_cf , 
    tjo2.offer_released_date_cf , tjo2.previous_salary_cf , tjo2.consultancy_fees_offered_cf , tjo.billing_per_month_cf 
from `tabEmployee Onboarding` teo 
inner join `tabJob Applicant` tja on tja.name = teo.job_applicant 
inner join `tabJob Opening` tjo on tjo.name = tja.job_title 
inner join `tabJob Offer` tjo2 on tjo2.name = teo.job_offer 
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
            "width": 180,
        },
        {
            "label": _("Client"),
            "fieldname": "customer_cf",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 180,
        },
        {
            "label": _("Technology"),
            "fieldname": "opportunity_technology_cf",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": _("Contact Person"),
            "fieldname": "customer_contact_cf",
            "fieldtype": "Link",
            "options": "Contact",
            "width": 180,
        },
        {
            "label": _("Onboarding Date"),
            "fieldname": "date_of_joining",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Location"),
            "fieldname": "location_cf",
            "width": 180,
        },
        {
            "label": _("Recruitment Office"),
            "fieldname": "npro_sourcing_owner_cf",
            "fieldtype": "Link",
            "options": "User",
            "width": 180,
        },
        {
            "label": _("Offer Sent Date"),
            "fieldname": "offer_released_date_cf",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Previous Salary"),
            "fieldname": "previous_salary_cf",
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "label": _("Consulting Fees Offered"),
            "fieldname": "consultancy_fees_offered_cf",
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "label": _("Billing"),
            "fieldname": "billing_per_month_cf",
            "fieldtype": "Currency",
            "width": 110,
        },
    ]


def get_conditions(filters):
    where_clause = []

    if filters.get("from_date"):
        where_clause.append("teo.date_of_joining >= %(from_date)s")
    if filters.get("till_date"):
        where_clause.append("teo.date_of_joining <= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
