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
        te.name employee, te.employee_name , tja.customer_cf , tcpo.post_boarding_status ,
        te.date_of_joining , te.billing_start_date_cf , te.npro_technical_manager_cf ,
        tt.subject , tt.status task_status , tt.completed_on , tt.name task_name , tt.task_owner_cf
        from `tabConsultant Post Onboarding` tcpo 
        inner join `tabEmployee Boarding Activity` teba on teba.parent = tcpo.name 
            and teba.parenttype = 'Consultant Post Onboarding'
        inner join tabEmployee te on te.name = tcpo.employee 
        inner join `tabJob Applicant` tja on tja.name = te.job_applicant 
        inner join tabProject tp on tp.name = tcpo.project 
        left outer join tabTask tt on tt.project = tcpo.project 
            and tt.subject like  concat(teba.activity_name,' : ','%%') 
        {where_conditions}
        """.format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        # debug=True,
    )

    return data


def get_columns(filters):
    return [
        {
            "label": _("Consultant Name"),
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
            "label": _("Status"),
            "fieldname": "post_boarding_status",
            "width": 100,
        },
        {
            "label": _("Onboarding Date"),
            "fieldname": "date_of_joining",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Billing Start Date"),
            "fieldname": "billing_start_date_cf",
            "fieldtype": "Date",
            "width": 130,
        },
        {
            "label": _("Activites"),
            "fieldname": "subject",
            "width": 280,
        },
        {
            "label": _("User"),
            "fieldname": "task_owner_cf",
            "width": 130,
        },
        {
            "label": _("Task Status"),
            "fieldname": "task_status",
            "width": 110,
        },
        {
            "label": _("Post Boarding Status"),
            "fieldname": "post_boarding_status",
            "width": 110,
        },
        {
            "label": _("Date Completed"),
            "fieldname": "completed_on",
            "fieldtype": "Date",
            "width": 130,
        },
    ]


def get_conditions(filters):
    where_clause = []

    # where_clause.append("tcpo.post_boarding_status in ('Pending','In Process') ")

    if filters.get("job_applicant"):
        where_clause.append("te.job_applicant = %(job_applicant)s")

    if filters.get("customer"):
        where_clause.append("tja.customer_cf = %(customer)s")

    if filters.get("task_status"):
        where_clause.append("tt.status = %(task_status)s")

    if filters.get("post_boarding_status"):
        where_clause.append("tcpo.post_boarding_status = %(post_boarding_status)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
