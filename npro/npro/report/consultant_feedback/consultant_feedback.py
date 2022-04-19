# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, today


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters):
    filters["today"] = today()
    data = frappe.db.sql(
        """
        select  
            ta.employee , ta.employee_name , te.npro_technical_manager_cf , ta.remarks ,
            tag.kra , tag.score , tag.score_earned , tja.customer_cf 
        from tabAppraisal ta 
        inner join `tabAppraisal Goal` tag on tag.parent = ta.name
        inner join tabEmployee te on te.name = ta.employee 
        inner join `tabJob Applicant` tja on tja.name = te.job_applicant 
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
            "label": _("Score Earned"),
            "fieldname": "score_earned",
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "label": _("Max Score"),
            "fieldname": "score",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": _("Parameters (KRA)"),
            "fieldname": "kra",
            "width": 300,
        },
        {
            "label": _("Remarks"),
            "fieldname": "remarks",
            "width": 300,
        },
    ]


def get_conditions(filters):
    where_clause = []

    # if filters.get("from_date"):
    #     where_clause.append("op.transaction_date >= %(from_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
