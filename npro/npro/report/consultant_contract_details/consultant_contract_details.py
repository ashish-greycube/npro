# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, today


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters):
    data = frappe.db.sql(
        """
    select 
	    te.job_applicant , te.employee_name , tja.customer_cf , 
	    tjo.billing_per_month_cf , tjo.sales_person_cf, te.contract_start_date_cf
		, te.contract_end_date , te.client_contract_start_date_cf , te.client_contract_end_date_cf 
    from tabEmployee te 
    inner join `tabJob Applicant` tja on tja.name = te.job_applicant 
    inner join `tabJob Opening` tjo on tjo.name = tja.job_title 
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
            "label": _("Billing"),
            "fieldname": "billing_per_month_cf",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": _("Client Contract Start Date"),
            "fieldname": "date_of_joining",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "label": _("Client Contract End Date"),
            "fieldname": "client_contract_start_date_cf",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "label": _("Consultant Contract Start Date"),
            "fieldname": "contract_start_date",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "label": _("Consultant Contract End Date"),
            "fieldname": "contract_end_date",
            "fieldtype": "Date",
            "width": 150,
        },
        {
            "label": _("Sales Person"),
            "fieldname": "sales_person_cf",
            "fieldtype": "Link",
            "options": "User",
            "width": 190,
        },
    ]


def get_conditions(filters):
    where_clause = []

    # if filters.get("from_date"):
    #     where_clause.append("op.transaction_date >= %(from_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
