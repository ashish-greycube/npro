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
            tja.name applicant, tja.applicant_name,  ti.designation, ti.scheduled_on, 
            tu.full_name interviewer, tir.interview_type, tja.status, 
            ti.average_rating, tir.expected_average_rating
        from 
            tabInterview ti 
            inner join `tabInterview Round` tir on tir.name = ti.interview_round 
            inner join `tabJob Applicant` tja on tja.name = ti.job_applicant 
            inner join `tabJob Opening` tjo on tjo.name = tja.job_title 
            inner join `tabInterview Detail` tid on tid.parent = ti.name
            inner join tabUser tu on tu.name = tid.interviewer 
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
            "label": _("Applicant Name"),
            "fieldname": "applicant_name",
            "width": 180,
        },
        {
            "label": _("Designation"),
            "fieldname": "designation",
            "fieldtype": "Link",
            "options": "Designation",
            "width": 130,
        },
        {
            "label": _("Scheduled On"),
            "fieldtype": "Date",
            "fieldname": "scheduled_on",
            "width": 130,
        },
        {
            "label": _("Interviewer"),
            "fieldname": "interviewer",
            "width": 180,
        },
        {
            "label": _("Interview Type"),
            "fieldname": "interview_type",
            "width": 120,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "width": 180,
        },
        {
            "label": _("Obtained Average Rating"),
            "fieldname": "average_rating",
            "fieldtype": "Int",
            "width": 180,
        },
        {
            "label": _("Expected Rating"),
            "fieldname": "expected_average_rating",
            "fieldtype": "Int",
            "width": 180,
        },
    ]


def get_conditions(filters):
    where_clause = []

    # if filters.get("from_date"):
    #     where_clause.append("op.transaction_date >= %(from_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
