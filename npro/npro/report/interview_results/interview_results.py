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
            tjo.customer_cf, tjo.job_title, tjo.description, tir.interview_type, 
            tif.interviewer_name_cf interviewer,
            tja.applicant_name, tjc.skill, tja.name applicant,
            tsa.rating obtained_rating, tjc.proficiency expected_rating, tif.feedback 
        from 
            tabInterview ti 
            inner join `tabInterview Round` tir on tir.name = ti.interview_round 
            inner join `tabJob Applicant` tja on tja.name = ti.job_applicant 
            inner join `tabJob Opening` tjo on tjo.name = tja.job_title 
            inner join `tabJRSS CT` tjc on tjc.parent = tjo.name
            left outer join `tabInterview Feedback` tif on tif.interview = ti.name 
            left outer join `tabSkill Assessment` tsa on tsa.parent = tif.name and tsa.skill = tjc.skill 
            {where_conditions}
        order by 
            ti.scheduled_on, tjo.name, tja.applicant_name
        """.format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
    )

    return data


def get_columns(filters):
    return [
        # tjo.customer_cf, tjo.job_title, tjo.description,
        # tir.interview_type, tif.interviewer_name_cf,
        # tja.applicant_name, tjc.skill,
        # tsa.rating obtained_rating, tjc.proficiency expected_rating, tif.feedback
        {
            "label": _("Customer"),
            "fieldname": "customer_cf",
            "width": 180,
        },
        {
            "label": _("Job Title"),
            "fieldname": "job_title",
            "width": 180,
        },
        {
            "label": _("Job Detail"),
            "fieldname": "description",
            "width": 180,
        },
        {
            "label": _("Interview Type"),
            "fieldname": "interview_type",
            "width": 120,
        },
        {
            "label": _("Interviewer"),
            "fieldname": "interviewer_name_cf",
            "width": 180,
        },
        {
            "label": _("Applicant Name"),
            "fieldname": "applicant_name",
            "width": 180,
        },
        {
            "label": _("Skill"),
            "fieldname": "skill",
            "width": 180,
        },
        {
            "label": _("Obtained Rating"),
            "fieldname": "obtained_rating",
            "fieldtype": "Int",
            "width": 180,
        },
        {
            "label": _("Expected Rating"),
            "fieldname": "expected_rating",
            "fieldtype": "Int",
            "width": 180,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "width": 180,
        },
    ]


def get_conditions(filters):
    where_clause = []

    # if filters.get("from_date"):
    #     where_clause.append("op.transaction_date >= %(from_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
