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
            tnms.customer , tnms.project ,
            tnms.overall_delivery_status , schedule_adherence , sla_adherence , major_achievements_for_the_month ,
            tnms.project_name , tp.npro_technical_manager_cf , tpu.consultants , tnms.customer_reporting_manager ,
            tnms.month_start_date , tnms.month_end_date
        from `tabNpro Monthly Status` tnms 
        inner join tabProject tp on tp.name = tnms.project 
        left outer join (select tpu.parent , GROUP_CONCAT(tpu.`user`) consultants from `tabProject User` tpu 
        group by tpu.parent ) tpu on tpu.parent = tp.name 
        {where_conditions}
        order by tp.name 
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
            "label": _("Client Name"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150,
        },
        {
            "label": _("Project Name"),
            "fieldname": "project_name",
            "width": 325,
        },
        {
            "label": _("Consultants Working on the Project"),
            "fieldname": "consultants",
            "width": 250,
        },
        {
            "label": _("Technical Manager"),
            "fieldname": "npro_technical_manager_cf",
            "fieldtype": "Data",
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
            "label": _("Overall Project Status"),
            "fieldname": "overall_delivery_status",
            "width": 140,
        },
        {
            "label": _("Schedule Adherence %"),
            "fieldname": "schedule_adherence",
            "width": 140,
        },
        {
            "label": _("SLA Adherence %"),
            "fieldname": "sla_adherence",
            "width": 140,
        },
        {
            "label": _("Major achievements for the months"),
            "fieldname": "major_achievements_for_the_month",
            "width": 260,
        },
        {
            "label": _("Month Start Date"),
            "fieldname": "month_start_date",
            "fieldtype": "Date",
            "width": 140,
        },
        {
            "label": _("Month End Date"),
            "fieldname": "month_end_date",
            "fieldtype": "Date",
            "width": 140,
        },
    ]


def get_conditions(filters):
    where_clause = []

    if filters.get("from_date"):
        where_clause.append("tnms.month_start_date >= %(from_date)s")

    if filters.get("till_date"):
        where_clause.append("tnms.month_end_date <= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
