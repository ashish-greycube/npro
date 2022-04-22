# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, today


def execute(filters=None):
    # from erpnext.projects.report.delayed_tasks_summary.delayed_tasks_summary import (
    #     execute,
    # )
    # columns, data, *args = execute(filters)
    return get_columns(filters), get_data(filters)


def get_data(filters):

    data = frappe.db.sql(
        """
        select 
            tt.name, tt.subject , tt.exp_start_date , tt.exp_end_date , tt.status task_status , tt.priority ,
            tt.completed_on , tt.progress , tt.task_owner_cf , tt.project ,
            case when tt.completed_on 
                then TIMESTAMPDIFF(DAY,tt.exp_end_date , tt.completed_on)
            when tt.status = 'Completed'
                then 0
            when tt.exp_end_date 
                then TIMESTAMPDIFF(DAY, tt.exp_end_date, NOW())
            else 0 end delay ,
            t1.job_applicant , te2.npro_technical_manager_cf , tp.status project_status
        from tabTask tt 
        inner join tabProject tp on tp.name = tt.project 
        left outer join (
        select job_applicant , project  from `tabEmployee Onboarding` teo 
        union all
        select te.job_applicant  , project  from `tabConsultant Post Onboarding` tcpo  
        inner join tabEmployee te on te.name = tcpo.employee ) t1 on t1.project = tt.project 
        left outer join tabEmployee te2 on te2.job_applicant = t1.job_applicant 
        {where_conditions}
        order by tt.project , tt.name
    """.format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
    )

    return data


def get_columns(filters):
    return [
        {
            "label": _("NPro Technical Manager"),
            "fieldname": "npro_technical_manager_cf",
            "width": 120,
        },
        {
            "fieldname": "project",
            "fieldtype": "Link",
            "label": _("Project"),
            "options": "Project",
            "width": 150,
        },
        {
            "fieldname": "task_owner_cf",
            "fieldtype": "Link",
            "label": _("Task Owner"),
            "options": "Employee",
            "width": 150,
        },
        {
            "fieldname": "project_status",
            "fieldtype": "Data",
            "label": _("Project Status"),
            "width": 100,
        },
        {
            "fieldname": "task_status",
            "fieldtype": "Data",
            "label": _("Task Status"),
            "width": 100,
        },
        {
            "fieldname": "name",
            "fieldtype": "Link",
            "label": _("Task"),
            "options": "Task",
            "width": 150,
        },
        {"fieldname": "subject", "fieldtype": "Data", "label": "Subject", "width": 200},
        {
            "fieldname": "priority",
            "fieldtype": "Data",
            "label": "Priority",
            "width": 80,
        },
        {
            "fieldname": "progress",
            "fieldtype": "Data",
            "label": "Progress (%)",
            "width": 120,
        },
        {
            "fieldname": "exp_start_date",
            "fieldtype": "Date",
            "label": "Expected Start Date",
            "width": 150,
        },
        {
            "fieldname": "exp_end_date",
            "fieldtype": "Date",
            "label": "Expected End Date",
            "width": 150,
        },
        {
            "fieldname": "completed_on",
            "fieldtype": "Date",
            "label": "Actual End Date",
            "width": 130,
        },
        {
            "fieldname": "delay",
            "fieldtype": "Data",
            "label": "Delay (In Days)",
            "width": 120,
        },
    ]


def get_conditions(filters):
    where_clause = []
    if filters.get("task_status"):
        where_clause.append("tt.status = %(task_status)s")
    if filters.get("priority"):
        where_clause.append("tt.priority = %(priority)s")

    if filters.get("from_date"):
        where_clause.append(
            "(tt.exp_end_date is null or tt.exp_end_date >= %(from_date)s)"
        )
    if filters.get("till_date"):
        where_clause.append(
            "(tt.exp_start_date is null or tt.exp_start_date <= %(till_date)s)"
        )

    return " where " + " and ".join(where_clause) if where_clause else ""
