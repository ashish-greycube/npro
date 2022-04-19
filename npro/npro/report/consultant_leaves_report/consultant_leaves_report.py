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
            te.name employee, te.employee_name , te.annual_leaves_allocated_cf , te.npro_technical_manager_cf ,
            tja.customer_cf , count(tntd.name) leaves_utilised
        from tabEmployee te 
        inner join `tabJob Applicant` tja on tja.name = te.job_applicant 
        inner join `tabNPro Timesheet` tnt on tnt.project in (
            select project from `tabEmployee Onboarding` teo where teo.job_applicant = te.job_applicant
        )
        left outer join `tabNPro Timesheet Detail` tntd  on tntd.parent = tnt.name and tntd.status like '%%leave%%'
        {where_conditions}
        group by te.name , te.employee_name , te.annual_leaves_allocated_cf , te.npro_technical_manager_cf ,
        tja.customer_cf 
        """.format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
    )

    for d in data:
        d["balance_leaves"] = d.annual_leaves_allocated_cf - (d.leaves_utilised or 0)

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
            "width": 120,
        },
        {
            "label": _("Total Leaves"),
            "fieldname": "annual_leaves_allocated_cf",
            "fieldtype": "Float",
            "width": 130,
        },
        {
            "label": _("Leaves Utilised"),
            "fieldname": "leaves_utilised",
            "fieldtype": "Float",
            "width": 130,
        },
        {
            "label": _("Leaves Left"),
            "fieldname": "balance_leaves",
            "fieldtype": "Float",
            "width": 130,
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
