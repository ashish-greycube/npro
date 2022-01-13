# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, today
import pandas as pd


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters):
    filters["today"] = today()
    data = frappe.db.sql(
        """
            select 
                tja.name applicant, tja.applicant_name, ti.designation, ti.scheduled_on, 
                TIME_FORMAT(ti.from_time,'%%h:%%i %%p') from_time, 
                TIME_FORMAT(ti.to_time,'%%h:%%i %%p') to_time,
                tu.full_name, ti.interview_round 
            from 
                tabInterview ti 
                inner join `tabJob Applicant` tja on tja.name = ti.job_applicant 
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
            "label": _("From Time"),
            "fieldname": "from_time",
            "width": 180,
        },
        {
            "label": _("To Time"),
            "fieldname": "to_time",
            "width": 180,
        },
        {
            "label": _("Interviewer"),
            "fieldname": "full_name",
            "width": 180,
        },
        {
            "label": _("Interview Round"),
            "fieldname": "interview_round",
            "fieldtype": "Link",
            "options": "Interview Round",
            "width": 120,
        },
    ]


def get_conditions(filters):
    where_clause = []
    where_clause.append("ti.scheduled_on >= %(today)s")

    # if filters.get("from_date"):
    #     where_clause.append("op.transaction_date >= %(from_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
