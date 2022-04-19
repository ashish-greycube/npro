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
            tes.employee_name , tja.customer_cf , te.npro_technical_manager_cf , te.relieving_date , 
            teba.activity_name , teba.`user` , tt.status , tt.act_end_date  , tjo.location_cf , 
            te.reason_for_leaving
        from `tabEmployee Separation` tes 
        inner join `tabEmployee Boarding Activity` teba on teba.parent = tes.name 
        inner join tabEmployee te on te.name = tes.employee 
        inner join `tabJob Applicant` tja on tja.name = te.job_applicant 
        inner join `tabJob Opening` tjo on tjo.name = tja.job_title  
        left outer join tabTask tt on tt.project = tes.project and tt.subject like concat(teba.activity_name, ' : ','%%') 
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
            "label": _("Consultant Name"),
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
            "label": _("NPro Technical Manager"),
            "fieldname": "npro_technical_manager_cf",
            "fieldtype": "Link",
            "options": "User",
            "width": 180,
        },
        {
            "label": _("Location"),
            "fieldname": "location_cf",
            "fieldtype": "Data",
            "width": 130,
        },
        {
            "label": _("Last Working Date"),
            "fieldname": "relieving_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Reason"),
            "fieldname": "reason_for_leaving",
            "width": 180,
        },
        {
            "label": _("Status"),
            "fieldname": "boarding_status",
            "width": 100,
        },
        {
            "label": _("User"),
            "fieldname": "user",
            "fieldtype": "Link",
            "options": "User",
            "width": 180,
        },
        {
            "label": _("Date Completed"),
            "fieldname": "act_end_date",
            "fieldtype": "Date",
            "width": 110,
        },
    ]


def get_conditions(filters):
    where_clause = []

    # if filters.get("from_date"):
    #     where_clause.append("op.transaction_date >= %(from_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
