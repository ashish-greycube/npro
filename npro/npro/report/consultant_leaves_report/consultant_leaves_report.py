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
                tp.customer , count(tntd.name) leaves_utilised
            from tabEmployee te 
            inner join `tabNPro Timesheet` tnt on tnt.consultant = te.name
            inner join tabProject tp on tp.name = tnt.project
            left outer join `tabNPro Timesheet Detail` tntd  on tntd.parent = tnt.name and tntd.status like '%%leave%%'
            {where_conditions}
            group by te.name , te.employee_name , te.annual_leaves_allocated_cf , te.npro_technical_manager_cf ,
            tp.customer
        """.format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        # debug=True,
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
            "fieldname": "customer",
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
            "(tntd.timesheet_date is null or tntd.timesheet_date >= %(from_date)s)"
        )
    if filters.get("till_date"):
        where_clause.append(
            "(tntd.timesheet_date is null or tntd.timesheet_date <= %(till_date)s)"
        )

    return " where " + " and ".join(where_clause) if where_clause else ""
