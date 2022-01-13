# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    columns, data = get_columns(filters), get_data(filters)

    if filters.get("interviewer"):
        columns[-2]["label"] = _("Interviewer's Rating")
        columns[-1]["hidden"] = 0
    return columns, data


def get_data(filters):
    data = frappe.db.sql(
        """
        select
        tja.name applicant, tja.applicant_name , tjo.customer_cf, tjc.skill, tjo.designation,
        tjc.proficiency proficiency_jrss, 
        coalesce(ir.rating/ir.interviewer_count,0) obtained_average_rating,
        ir.interviewers
        from `tabJob Applicant` tja 
        inner join `tabJob Opening` tjo on tjo.name = tja.job_title 
        inner join `tabJRSS CT` tjc on tjc.parent = tjo.name 
        left outer join (
            select ti.job_applicant, ti.job_opening, ti.interview_round,
            tsa.skill, sum(ifnull(tsa.rating,0)) rating, 
            count(tif.interviewer) interviewer_count, concat_ws(',', tif.interviewer_name_cf) interviewers
            ,tif.interview 
            from tabInterview ti 
            left outer join `tabInterview Feedback` tif on tif.interview = ti.name
            left outer join `tabSkill Assessment` tsa on tsa.parent = tif.name
            {where_conditions}
            group by ti.job_applicant, ti.job_opening, 
            tsa.skill, tif.interview, ti.interview_round
        ) ir on tjc.skill = ir.skill and ir.job_applicant = tja.name 
        {job_opening_filters}
""".format(
            where_conditions=get_conditions(filters),
            job_opening_filters=get_job_conditions(filters),
        ),
        filters,
        as_dict=1,
    )

    return data


def get_columns(filters):
    return [
        {
            "label": _("Customer"),
            "fieldname": "customer_cf",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 220,
        },
        {
            "label": _("Designation"),
            "fieldname": "designation",
            "fieldtype": "Link",
            "options": "Designation",
            "width": 180,
        },
        {
            "label": _("Applicant"),
            "fieldname": "applicant_name",
            "fieldtype": "Link",
            "options": "Job Applicant",
            "width": 220,
        },
        {
            "label": _("Skill"),
            "fieldname": "skill",
            "fieldtype": "Link",
            "options": "Skill",
            "width": 220,
        },
        {
            "label": _("Proficiency Expected"),
            "fieldname": "proficiency_jrss",
            "fieldtype": "Int",
            "width": 175,
        },
        # {
        #     "label": _("Interview Proficiency Expected"),
        #     "fieldname": "proficiency_interview_round",
        #     "fieldtype": "Int",
        #     "width": 175,
        # },
        {
            "label": _(
                "Obtained Average of all Interviewers (Obtained Average Rating)"
            ),
            "fieldname": "obtained_average_rating",
            "fieldtype": "Int",
            "width": 175,
        },
        {
            "label": _("Interviewer"),
            "fieldname": "interviewers",
            "fieldtype": "Data",
            "width": 200,
            "hidden": 1,
        },
    ]


def get_conditions(filters):
    where_clause = []
    if filters.get("interviewer"):
        where_clause.append("tif.interviewer = %(interviewer)s")
    return " where " + " and ".join(where_clause) if where_clause else ""


def get_job_conditions(filters):
    where_clause = []
    if filters.get("interviewer"):
        where_clause.append("ir.interviewers <> ''")
    if filters.get("job_opening"):
        where_clause.append("tjo.name = %(job_opening)s")

    return " where " + " and ".join(where_clause) if where_clause else ""


@frappe.whitelist()
def get_interviewers(filters=None):
    return [""] + [
        d[0]
        for d in frappe.db.sql(
            """ 
        select distinct(user) from tabInterviewer ti
		""",
            as_list=1,
        )
    ]
