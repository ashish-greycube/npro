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
tncws.name, tncws.week_start_date, tncws.npro_technical_manager, tncws.project, tncws.week_end_date, 
tncws.customer, tp.customer_reporting_mgr_cf , tncws.schedule_adherence, tncws.code_review_count, tncws.
task_resolved_in_week, tncws.task_resolved_expectation, tncws.project_status, tncws.
client_specific_issue, tncws.sla_adherence, tncws.tec_doc_rev, tncws.task_incomplete, tncws.
rework_done, tncws.extra_achievement_of_week, tncws.outstanding_invoices ,
tp.project_name , tpu.consultants
from 
    `tabNpro Client Weekly Status` tncws 
    inner join tabProject tp on tp.name = tncws.project
    left outer join (
        select tpu.parent , GROUP_CONCAT(tpu.`user`) consultants 
        from `tabProject User` tpu 
        group by tpu.parent ) tpu on tpu.parent = tp.name     
order by name
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
            "label": _("Client Name"),
            "fieldname": "customer",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Customer Reporting Manager"),
            "fieldname": "customer_reporting_mgr_cf",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Project Name"),
            "fieldname": "project_name",
            "fieldtype": "Data",
            "width": 350,
        },
        {
            "label": _("Consultants"),
            "fieldname": "consultants",
            "fieldtype": "Data",
            "width": 250,
        },
        {
            "label": _("Technical Manager"),
            "fieldname": "npro_technical_manager",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("No of Tasks/ Issues Resolved in the week,"),
            "fieldname": "task_resolved_in_week",
            "fieldtype": "Int",
            "width": 150,
        },
        {
            "label": _("No of Tasks/ Issues planned not completed,"),
            "fieldname": "task_incomplete",
            "fieldtype": "Int",
            "width": 150,
        },
        {
            "label": _("No of Tasks/Issues Resolved above expectation,"),
            "fieldname": "task_resolved_expectation",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Over all Project status"),
            "fieldname": "project_status",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Any specific issues which needs clients attention"),
            "fieldname": "client_specific_issue",
            "fieldtype": "Data",
            "width": 150,
        },
    ]


def get_conditions(filters):
    where_clause = []

    # if filters.get("from_date"):
    #     where_clause.append("op.transaction_date >= %(from_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
