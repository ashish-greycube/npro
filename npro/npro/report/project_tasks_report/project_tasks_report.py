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
	tpu.candidate_name , tp.name project, tp.customer , tp.customer_reporting_mgr_cf ,
	tp.project_name , tp.status project_status , tp.expected_start_date , tp.percent_complete , 
	tt.name task_name, tt.subject , coalesce(tt.parent_task,'') parent_task , ptt.subject parent_subject , 
    tp.npro_technical_manager_cf , tt.status task_status , tt.task_owner_cf ,
	tt.exp_start_date , tt.exp_end_date , tt.task_issue_cf , tt.progress
from tabProject tp 
left outer join (select tpu.parent , GROUP_CONCAT(tpu.`user`) candidate_name from `tabProject User` tpu 
group by tpu.parent ) tpu on tpu.parent = tp.name 
inner join tabTask tt on tt.project = tp.name 
left outer join tabTask ptt on ptt.name = tt.parent_task
{where_conditions}
order by tp.name, tt.name 
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
        # {
        #     "label": _("Candidate Name"),
        #     "fieldname": "candidate_name",
        #     "fieldtype": "Data",
        #     "width": 200,
        # },
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
            "label": _("Project ID"),
            "fieldtype": "Link",
            "fieldname": "project",
            "options": "Project",
            "width": 125,
        },
        {
            "label": _("Project Name"),
            "fieldname": "project_name",
            "width": 325,
        },
        {
            "label": _("Project Start Date"),
            "fieldname": "expected_start_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Task"),
            "fieldname": "subject",
            "width": 255,
        },
        {
            "label": _("Parent Task"),
            "fieldname": "parent_subject",
            "width": 195,
        },
        {
            "label": _("Task Owner"),
            "fieldname": "task_owner_cf",
            "fieldtype": "Link",
            "options": "User",
            "width": 100,
        },
        {
            "label": _("Task Status"),
            "fieldname": "task_status",
            "width": 100,
        },
        {
            "label": _("Task Start Date"),
            "fieldname": "exp_start_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Task End Date"),
            "fieldname": "exp_end_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("% Progress"),
            "fieldname": "progress",
            "fieldtype": "Percent",
            "width": 110,
        },
        {
            "label": _("Project %"),
            "fieldname": "percent_complete",
            "fieldtype": "Percent",
            "width": 110,
        },
        {
            "label": _("Issues"),
            "fieldname": "task_issue_cf",
            "width": 200,
        },
    ]


def get_conditions(filters):
    where_clause = []

    if filters.get("project"):
        where_clause.append("tp.name = %(project)s")

    if filters.get("project_type"):
        where_clause.append("tp.project_type = %(project_type)s")

    if filters.get("from_date"):
        where_clause.append("DATE(tt.creation) >= %(from_date)s")

    if filters.get("to_date"):
        where_clause.append("DATE(tt.creation) <= %(to_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
