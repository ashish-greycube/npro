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
            with fn as ( 
	            select tnt.consultant , count(tntd.name) ct
	            from `tabNPro Timesheet` tnt
	            inner join `tabNPro Timesheet Detail` tntd on tntd.parent = tnt.name and tntd.status like '%%leave%%'
                {where_conditions}
	            group by tnt.consultant
            )
            select 
            	te.name employee, te.employee_name , te.annual_leaves_allocated_cf , te.customer_cf ,
            	fn.ct leaves_utilised , te.annual_leaves_allocated_cf - fn.ct  balance_leaves
            from tabEmployee te
            left outer join fn on fn.consultant = te.name
            where te.status = 'Active'
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
