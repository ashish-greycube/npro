# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
import pandas as pd


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters):
    data = frappe.db.sql(
        """
        select 
            tja.name applicant, tjo.name job_name, tja.applicant_name, tja.source, 
            tja.status, tja.previous_company_cf, tja.applicant_total_experience_cf,
            tja.rejected_reason_cf,
            tjo.job_title, tjo.customer_cf,
            concat_ws(' - ', round(tja.lower_range), round(tja.upper_range)) salary_range,
            tif.name feedback_name, tif.interviewer_name_cf, tif.interview_round, tif.feedback,
            tif.average_rating interviewer_scoring, tjc.proficiency expected_scoring
        from `tabJob Applicant` tja 
        inner join `tabJob Opening` tjo on tjo.name = tja.job_title 
        left outer join (
	        select parent, avg(proficiency) proficiency from `tabJRSS CT` tjc 
	        group by parent
        ) tjc on tjc.parent = tjo.name 
        left outer join tabInterview ti on ti.job_applicant = tja.name and ti.job_opening =tja.job_title 
        left outer join `tabInterview Feedback` tif on tif.interview = ti.name
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
            "label": _("Job Opening"),
            "fieldname": "job_name",
            "fieldtype": "Link",
            "options": "Job Opening",
            "width": 130,
        },
        {
            "label": _("Customer"),
            "fieldname": "customer_cf",
            "width": 200,
        },
        {
            "label": _("Technology"),
            "fieldname": "job_title",
            "width": 200,
        },
        {
            "label": _("Source"),
            "fieldname": "source",
            "width": 180,
        },
        {
            "label": _("Total Experience"),
            "fieldname": "applicant_total_experience_cf",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Expected Salary Range"),
            "fieldname": "salary_range",
            "width": 180,
        },
        {
            "label": _("Interviewer"),
            "fieldname": "interviewer_name_cf",
            "width": 180,
        },
        {
            "label": _("Expected Scoring"),
            "fieldname": "expected_scoring",
            "fieldtype": "Int",
            "width": 180,
        },
        {
            "label": _("Interviewer Scoring"),
            "fieldname": "interviewer_scoring",
            "fieldtype": "Int",
            "width": 180,
        },
        {
            "label": _("Feedback"),
            "fieldname": "feedback",
            "width": 180,
        },
        #         {
        #     "label": _("Link to Feedback"),
        #     "fieldname": "feedback_name",
        #     "fieldtype": "Link",
        #     "options": "Interview Feedback",
        #     "width": 130,
        # },
        # {
        #     "label": _("Interview Round"),
        #     "fieldname": "interview_round",
        #     "fieldtype": "Link",
        #     "options": "Interview Round",
        #     "width": 120,
        # },
    ]


def get_conditions(filters):
    where_clause = []
    where_clause.append("tja.status = 'Accepted'")

    # if filters.get("from_date"):
    #     where_clause.append("op.transaction_date >= %(from_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
