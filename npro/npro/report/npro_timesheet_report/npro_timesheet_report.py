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
            tnt.consultant , tnt.project , tnt.role , tnt.from_date , tnt.to_date , 
            tnt.client_manager , tnt.name , tntd.hours, tntd.remark , tntd.status , 
            tntd.timesheet_date, DATE_FORMAT(tntd.timesheet_date,'%%a') day_name , 
            te.job_applicant , te.employee_name , tja.customer_cf , tnt.project_name
        from `tabNPro Timesheet` tnt 
        inner join `tabNPro Timesheet Detail` tntd  on tntd.parent = tnt.name
        inner join `tabEmployee` te on te.name = tnt.consultant 
        inner join `tabJob Applicant` tja on tja.name = te.job_applicant 
        {where_conditions}
        order by project, timesheet_date
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
            "label": _("Consultant"),
            "fieldname": "consultant",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 200,
        },
        {
            "label": _("Client"),
            "fieldname": "customer_cf",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 180,
        },
        {
            "label": _("Project"),
            "fieldname": "project_name",
            "width": 240,
        },
        {
            "label": _("Role"),
            "fieldname": "role",
            "width": 120,
        },
        {
            "label": _("Client Manager"),
            "fieldname": "client_manager",
            "width": 180,
        },
        {
            "label": _("Date"),
            "fieldtype": "Date",
            "fieldname": "timesheet_date",
            "width": 110,
        },
        {
            "label": _("Day"),
            "fieldname": "day_name",
            "width": 80,
        },
        {
            "label": _("Hours"),
            "fieldtype": "Float",
            "fieldname": "hours",
            "width": 120,
        },
    ]


def get_conditions(filters):
    where_clause = []

    if filters.get("from_date"):
        where_clause.append("tntd.timesheet_date >= %(from_date)s")

    if filters.get("till_date"):
        where_clause.append("tntd.timesheet_date <= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
