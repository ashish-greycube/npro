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
                teo.job_applicant , teo.employee , teo.employee_name , teo.date_of_joining , teo.boarding_status ,
                tja.customer_cf , teba.user , tu.full_name ,
                tjo.opportunity_technology_cf , tjo.location_cf ,
                tt.subject , tt.status task_status , tt.completed_on 
            from `tabEmployee Onboarding` teo 
            inner join `tabEmployee Boarding Activity` teba on teba.parent = teo.name and teba.parenttype = 'Employee Onboarding'
            inner join `tabJob Applicant` tja on tja.name = teo.job_applicant 
            inner join `tabJob Opening` tjo on tjo.name = tja.job_title 
            inner join tabProject tp on tp.name = teo.project 
            left outer join tabTask tt on tt.project = teo.project and tt.subject like  concat(teba.activity_name,' : ','%%') 
            left outer join tabUser tu on tu.name = teba.`user` 
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
            "fieldname": "job_applicant",
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
            "label": _("Status"),
            "fieldname": "boarding_status",
            "width": 100,
        },
        {
            "label": _("Technology"),
            "fieldname": "opportunity_technology_cf",
            "fieldtype": "Data",
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
            "label": _("User"),
            "fieldname": "full_name",
            "width": 130,
        },
        {
            "label": _("Task Status"),
            "fieldname": "task_status",
            "width": 110,
        },
        {
            "label": _("Date Completed"),
            "fieldname": "completed_on",
            "fieldtype": "Date",
            "width": 110,
        },
    ]


def get_conditions(filters):
    where_clause = []

    where_clause.append("teo.boarding_status in ('Pending','In Process') ")

    if filters.get("job_applicant"):
        where_clause.append("teo.job_applicant = %(job_applicant)s")

    if filters.get("customer"):
        where_clause.append("tja.customer_cf = %(customer)s")

    if filters.get("task_status"):
        where_clause.append("tt.status = %(task_status)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
