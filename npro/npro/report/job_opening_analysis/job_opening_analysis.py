# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe


import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    columns, data = get_columns(filters), get_data(filters)

    return columns, data


def get_data(filters):
    data = frappe.db.sql(
        """
        with npro_screening_passed as
        (
            select distinct doc_name
            from `tabNPro Status Log` tnsl 
            where new_value in (
                'Technical interview', 'Technical interview- Rejected', 'Client CV Screening', 
                'Client CV Screening- Accepted', 'Client CV Screening- Rejected', 'Client Interview', 
                'Client interview-Rejected', 'Client Interview-rescheduled', 
                'Client Interview-waiting for feedback', 'Rejected by candidate', 'Hold', 'Accepted'
            )
        ),
        cv_shared as
        (
            select distinct doc_name
            from `tabNPro Status Log` tnsl 
            where new_value in (
                'Client CV Screening', 'Client CV Screening- Accepted', 'Client CV Screening- Rejected', 
                'Client Interview', 'Client interview-Rejected', 'Client Interview-rescheduled', 
                'Client Interview-waiting for feedback', 'Rejected by candidate', 'Hold', 'Accepted'
            )
        ),
        cv_accepted_by_client as
        (
            select distinct doc_name
            from `tabNPro Status Log` tnsl 
            where new_value in (
            'Client CV Screening- Accepted', 'Client Interview', 'Client interview-Rejected', 
            'Client Interview-rescheduled', 'Client Interview-waiting for feedback', 
            'Rejected by candidate', 'Hold', 'Accepted')
        ),
        cv_rejected_by_client as
        (
            select distinct doc_name
            from `tabNPro Status Log` tnsl 
            where new_value in ('Client CV Screening- Rejected')
        ),
        client_interview_held as
        (
            select distinct doc_name
            from `tabNPro Status Log` tnsl 
            where new_value in ('Client interview-Rejected', 
            'Client Interview-waiting for feedback' , 'Accepted' , 'Hold' )
        ),
        client_interview_rejected as
        (
            select distinct doc_name
            from `tabNPro Status Log` tnsl 
            where new_value in ('Client interview-Rejected')
        ),
        cand_selected as
        (
            select distinct doc_name
            from `tabNPro Status Log` tnsl 
            where new_value in ('Accepted')
        )
		select 
        	tjo.name job_opening, tjo.job_title, tjo.company, tjo.designation ,
        	tjo.customer_cf , tjo.customer_contact_cf , tjo.npro_sourcing_owner_cf , tjo.sales_person_cf ,
            appl.applied , t1.passed_npro_screening , t1.no_cv_shared ,t1.cv_accepted_by_client ,
            t1.cv_rejected_by_client , t1.client_interview_held , t1.client_interview_rejected
        from `tabJob Opening` tjo 
        left outer join 
        (
            select tja.job_title 
            , count(distinct npro_screening_passed.doc_name) passed_npro_screening
            , count(distinct cv_shared.doc_name) no_cv_shared
            , count(distinct cv_accepted_by_client.doc_name) cv_accepted_by_client
            , count(distinct cv_rejected_by_client.doc_name) cv_rejected_by_client
            , count(distinct client_interview_held.doc_name) client_interview_held
            , count(distinct client_interview_rejected.doc_name) client_interview_rejected
            from `tabJob Applicant` tja 
            left outer join npro_screening_passed on tja.name = npro_screening_passed.doc_name
            left outer join cv_shared on tja.name = cv_shared.doc_name
            left outer join cv_accepted_by_client on tja.name = cv_accepted_by_client.doc_name
            left outer join cv_rejected_by_client on tja.name = cv_rejected_by_client.doc_name
            left outer join client_interview_held on tja.name = client_interview_held.doc_name
            left outer join client_interview_rejected on tja.name = client_interview_rejected.doc_name
            left outer join cand_selected on tja.name = cand_selected.doc_name
            where date(tja.creation) >= %(from_date)s and date(tja.creation) <= %(to_date)s
            group by tja.job_title 
        ) t1 on t1.job_title = tjo.name
        left outer join (
            select job_title , count(name) applied
            from `tabJob Applicant`
            group by job_title
        ) appl on appl.job_title = tjo.name
        {where_conditions}
order by tjo.creation 
""".format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        debug=True,
    )

    return data


# def get_data(filters):
#     data = frappe.db.sql(
#         """
# WITH t1 as
# (
# 		select tja.job_title , tnsl.new_value status, count(tnsl.new_value) ct
#         from `tabJob Applicant` tja
#         inner join `tabNPro Status Log` tnsl on tnsl.doc_type = 'Job Applicant'
#             and tnsl.docfield_name = 'status' and tnsl.doc_name = tja.name
#             and date(tnsl.creation) >= %(from_date)s and date(tnsl.creation) <= %(to_date)s
#         where
#             date(tja.creation) >= %(from_date)s and date(tja.creation) <= %(to_date)s
# 		group by tja.job_title , tnsl.new_value
# 		order by tja.job_title , tnsl.new_value
# )
# select
# 	tjo.name job_opening, tjo.job_title, tjo.company, tjo.designation ,
# 	tjo.customer_cf , tjo.customer_contact_cf , tjo.npro_sourcing_owner_cf , tjo.sales_person_cf ,
# 	max(appl.applied) cand_applied ,
# 	sum(case when t1.status in (
#         'Technical interview',
#         'Technical interview- Rejected',
#         'Client CV Screening',
#         'Client CV Screening- Accepted',
#         'Client CV Screening- Rejected',
#         'Client Interview',
#         'Client interview-Rejected',
#         'Client Interview-rescheduled',
#         'Client Interview-waiting for feedback',
#         'Rejected by candidate',
#         'Hold',
#         'Accepted'
#     ) then 1 else 0 end) cand_passed_npro_screening ,
# 	sum(case when t1.status in (
#         'Client CV Screening',
#         'Client CV Screening- Accepted',
#         'Client CV Screening- Rejected',
#         'Client Interview',
#         'Client interview-Rejected',
#         'Client Interview-rescheduled',
#         'Client Interview-waiting for feedback',
#         'Rejected by candidate',
#         'Hold',
#         'Accepted'
#     ) then 1 else 0 end) no_cv_shared ,
# 	sum(case when t1.status in (
#         'Client CV Screening- Accepted',
#         'Client Interview',
#         'Client interview-Rejected',
#         'Client Interview-rescheduled',
#         'Client Interview-waiting for feedback',
#         'Rejected by candidate',
#         'Hold',
#         'Accepted'
#     ) then 1 else 0 end) cv_accepted_by_client ,
# 	sum(case when t1.status in ('CV rejected by client') then 1 else 0 end) cv_rejected_by_client ,
#     sum(case when t1.status in (
#         'Client interview-Rejected',
#         'Client Interview-waiting for feedback' ,
#         'Accepted' ,
#         'Hold'
#     ) then 1 else 0 end) client_interview_held ,
# 	sum(case when t1.status in ('Client interview-Rejected') then 1 else 0 end) client_interview_rejected ,
# 	sum(case when t1.status in ('Accepted') then 1 else 0 end) selected
# from `tabJob Opening` tjo
# left outer join t1 on t1.job_title = tjo.name
# left outer join
# (
#     select count(tja.name) applied, tjo.name
#     from `tabJob Applicant` tja
#     inner join `tabJob Opening` tjo on tjo.name = tja.job_title
#     group by tjo.name
# ) appl on appl.name = tjo.name
# {where_conditions}
# group by
# 	job_opening, tjo.job_title, tjo.company, tjo.designation ,
# 	tjo.customer_cf , tjo.customer_contact_cf , tjo.npro_sourcing_owner_cf , tjo.sales_person_cf
# order by tjo.creation
# """.format(
#             where_conditions=get_conditions(filters),
#         ),
#         filters,
#         as_dict=True,
#         debug=True,
#     )

# return data


def get_columns(filters):
    return [
        {
            "label": "Customer",
            "fieldname": "customer_cf",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 190,
        },
        {
            "label": "Customer Contact",
            "fieldname": "customer_contact_cf",
            "fieldtype": "Link",
            "options": "Contact",
            "width": 190,
        },
        {
            "label": "Job Opening",
            "fieldname": "job_opening",
            "fieldtype": "Link",
            "options": "Job Opening",
            "width": 190,
        },
        {
            "label": "NPro Sourcing Owner",
            "fieldname": "npro_sourcing_owner_cf",
            "fieldtype": "Link",
            "options": "User",
            "width": 190,
        },
        {
            "label": "Npro Sales Person",
            "fieldname": "sales_person_cf",
            "fieldtype": "Link",
            "options": "User",
            "width": 190,
        },
        {
            "label": "Candidates Applied",
            "fieldname": "applied",
            "width": 190,
        },
        {
            "label": "Candidates Passed NPro Screening",
            "fieldname": "passed_npro_screening",
            "width": 275,
        },
        {
            "label": "Candidate passed Npro technical interview",
            "fieldname": "no_cv_shared",
            "width": 290,
        },
        {
            "label": "No Of CV Shared",
            "fieldname": "no_cv_shared",
            "width": 190,
        },
        {
            "label": "CV Accepted by Client",
            "fieldname": "cv_accepted_by_client",
            "width": 190,
        },
        {
            "label": "CV Rejected by Client",
            "fieldname": "cv_rejected_by_client",
            "width": 190,
        },
        {
            "label": "Client Interview held",
            "fieldname": "client_interview_held",
            "width": 190,
        },
        {
            "label": "Client interview-Rejected",
            "fieldname": "client_interview_rejected",
            "width": 190,
        },
        {
            "label": "Selected",
            "fieldname": "selected",
            "width": 145,
        },
    ]


def get_conditions(filters):
    where_clause = []
    if filters.get("job_opening"):
        where_clause.append("tjo.name = %(job_opening)s")
    if filters.get("customer"):
        where_clause.append("tjo.customer_cf = %(customer)s")

    return " where " + " and ".join(where_clause) if where_clause else ""


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_customers(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql(
        """ select distinct customer_cf 
        from `tabJob Opening` 
        where customer_cf like %(txt)s
        limit %(start)s, %(page_len)s""",
        {
            "start": start,
            "page_len": page_len,
            "txt": "%%%s%%" % txt,
        },
    )
