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
            tnws.customer , tnws.customer_reporting_manager , tnws.project ,
            tnws.project_name , tpu.consultants , tnws.npro_technical_manager , 
            tnws.escalation_mgmt_count , tnws.issues_needs_attention , tnws.total_expected_hours , 
            tnws.total_hours_worked , tnws.status_rag , tnws.week_start_date , tnws.week_end_date 
        from `tabNPro Weekly Status` tnws 
        inner join tabProject tp on tp.name = tnws.project 
        left outer join (select tpu.parent , GROUP_CONCAT(tpu.`user`) consultants from `tabProject User` tpu 
        group by tpu.parent) tpu on tpu.parent = tp.name 
        {where_conditions}
        order by tnws.week_start_date , tnws.project 
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
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150,
        },
        {
            "label": _("Customer Reporting Manager"),
            "fieldname": "customer_reporting_manager",
            "fieldtype": "Link",
            "options": "User",
            "width": 130,
        },
        {
            "label": _("Project Name"),
            "fieldname": "project_name",
            "width": 325,
        },
        {
            "label": _("Consultants"),
            "fieldname": "consultants",
            "width": 250,
        },
        {
            "label": _("Technical Manager"),
            "fieldname": "npro_technical_manager",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Escalations Managed"),
            "fieldname": "escalation_mgmt_count",
            "width": 255,
        },
        {
            "label": _("Issues need Attention"),
            "fieldname": "issues_needs_attention",
            "width": 255,
        },
        {
            "label": _("Total Expected Hours"),
            "fieldname": "total_expected_hours",
            "fieldtype": "Float",
            "width": 130,
        },
        {
            "label": _("Total Hours Worked"),
            "fieldname": "total_hours_worked",
            "fieldtype": "Float",
            "width": 130,
        },
        {
            "label": _("Status RAG"),
            "fieldname": "status_rag",
            "width": 195,
        },
        {
            "label": _("Week Start Date"),
            "fieldname": "week_start_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Week End Date"),
            "fieldname": "week_end_date",
            "fieldtype": "Date",
            "width": 120,
        },
    ]


def get_conditions(filters):
    where_clause = []

    if filters.get("from_date"):
        where_clause.append("tnws.week_start_date >= %(from_date)s")

    if filters.get("till_date"):
        where_clause.append("tnws.week_end_date <= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
