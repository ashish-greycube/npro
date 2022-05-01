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
            tt.employee_name , tt.employee , tp.customer , tp.customer_reporting_mgr_cf ,
            ttd.project , tp.project_name , DATE(tp.actual_start_date) actual_start_date , 
            DATE(ttd.from_time) ttd_date , ttd.task , ttk.subject ,
            sum(ttd.hours) hours , ttk.no_of_issues_escalated_cf , ttk.issues_escalated_desc_cf 
                from tabTimesheet tt 
            left outer join `tabTimesheet Detail` ttd on ttd.parent = tt.name 
            left outer join tabProject tp on tp.name = ttd.project 
            left outer join tabTask ttk on ttk.name = ttd.task 
            {where_conditions}
            group by tt.employee_name , tt.employee , tp.customer , 
            ttd.project , tp.project_name , DATE(tp.actual_start_date) , 
            DATE(ttd.from_time) , ttd.task , ttk.subject ,
            ttk.no_of_issues_escalated_cf , ttk.issues_escalated_desc_cf 
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
            "width": 200,
        },
        {
            "label": _("Client"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200,
        },
        {
            "label": _("Reporting Manager"),
            "fieldname": "customer_reporting_mgr_cf",
            "width": 190,
        },
        {
            "label": _("Project Name"),
            "fieldname": "project_name",
            "width": 325,
        },
        {
            "label": _("Project Start Date"),
            "fieldname": "actual_start_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Date"),
            "fieldname": "ttd_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Task"),
            "fieldname": "subject",
            "width": 255,
        },
        {
            "label": _("No. of hrs worked"),
            "fieldtype": "Float",
            "fieldname": "hours",
            "width": 110,
        },
        {
            "label": _("No of Critical issues not addressed and escalations by Client"),
            "fieldname": "no_of_issues_escalated_cf",
            "fieldtype": "Int",
            "width": 150,
        },
        {
            "label": _(
                "Critical Issues not addressed & escalation by Client- Description"
            ),
            "fieldname": "issues_escalated_desc_cf",
            "width": 100,
        },
    ]


def get_conditions(filters):
    where_clause = []

    if filters.get("from_date"):
        where_clause.append("ttd.from_time >= %(from_date)s")

    if filters.get("till_date"):
        where_clause.append("ttd.from_time <= %(till_date)s")

    if filters.get("candidate"):
        where_clause.append("tt.employee = %(candidate)s")

    if filters.get("project"):
        where_clause.append("tp.name = %(project)s")

    if filters.get("client"):
        where_clause.append("tp.customer = %(client)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
