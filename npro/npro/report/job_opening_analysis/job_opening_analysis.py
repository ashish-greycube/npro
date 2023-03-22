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
    if filters.get("ignore_duration"):
        filters["from_date"] = "1900-01-01"
        filters["to_date"] = "2500-01-01"

    filters["ignore_duration"] = filters.get("ignore_duration") or 0

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
                'Client Interview-waiting for feedback', 'Rejected by Candidate', 'Hold', 'Accepted'
            )
        ),
        cv_shared as
        (
            select distinct doc_name
            from `tabNPro Status Log` tnsl 
            where new_value in (
                'Client CV Screening', 'Client CV Screening- Accepted', 'Client CV Screening- Rejected', 
                'Client Interview', 'Client interview-Rejected', 'Client Interview-rescheduled', 
                'Client Interview-waiting for feedback', 'Rejected by Candidate', 'Hold', 'Accepted'
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
        rejected_by_candidate as
        (
            select distinct doc_name
            from `tabNPro Status Log` tnsl 
            where new_value in ('Rejected by Candidate')
        ),        
        cand_selected as
        (
            select distinct doc_name
            from `tabNPro Status Log` tnsl 
            where new_value in ('Accepted')
        )
		select 
        	tjo.name job_opening, tjo.job_title, tjo.company, tjo.designation , tjo.location_cf ,
        	tjo.customer_cf , tjo.customer_contact_cf , tjo.npro_sourcing_owner_cf , tjo.sales_person_cf ,
            appl.applied , t1.passed_npro_screening , t1.no_cv_shared ,t1.cv_accepted_by_client ,
            t1.cv_rejected_by_client , t1.client_interview_held , t1.client_interview_rejected , t1.selected ,
            t1.rejected_by_candidate ,
        t1.passed_npro_screening + t1.no_cv_shared + t1.cv_accepted_by_client + 
        t1.cv_rejected_by_client +  t1.client_interview_held +  
        t1.client_interview_rejected +  t1.selected + t1.rejected_by_candidate total_count
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
            , count(distinct rejected_by_candidate.doc_name) rejected_by_candidate
            , count(distinct cand_selected.doc_name) selected
            from `tabJob Applicant` tja 
            left outer join npro_screening_passed on tja.name = npro_screening_passed.doc_name
            left outer join cv_shared on tja.name = cv_shared.doc_name
            left outer join cv_accepted_by_client on tja.name = cv_accepted_by_client.doc_name
            left outer join cv_rejected_by_client on tja.name = cv_rejected_by_client.doc_name
            left outer join client_interview_held on tja.name = client_interview_held.doc_name
            left outer join client_interview_rejected on tja.name = client_interview_rejected.doc_name
            left outer join rejected_by_candidate on tja.name = rejected_by_candidate.doc_name
            left outer join cand_selected on tja.name = cand_selected.doc_name
            where date(tja.modified) >= %(from_date)s and date(tja.modified) <= %(to_date)s
            group by tja.job_title 
        ) t1 on t1.job_title = tjo.name
        left outer join (
            select tja.job_title , count(tja.name) applied
            from `tabJob Applicant` tja
            where date(tja.modified) >= %(from_date)s and date(tja.modified) <= %(to_date)s
            group by job_title
        ) appl on appl.job_title = tjo.name
        left outer join(
    	    select job_title, count(*) ct from `tabNPro Status Log` tnsl
            inner join `tabJob Applicant` tja on tja.name = tnsl.doc_name 
            group by tja.job_title
        ) t3 on t3.job_title = tjo.name
        {where_conditions}
order by tjo.creation 
""".format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        debug=True,
    )
    if not filters.get("ignore_duration"):
        data = [d for d in data if d.get("total_count")]

    return data


def get_conditions(filters):
    where_clause = []
    if filters.get("job_opening"):
        where_clause.append("tjo.name = %(job_opening)s")
    if filters.get("customer"):
        where_clause.append("tjo.customer_cf = %(customer)s")

    return " and " + " and ".join(where_clause) if where_clause else ""


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
            "width": 120,
        },
        {
            "label": "Job Title",
            "fieldname": "job_title",
            "fieldtype": "Data",
            "width": 230,
        },
        {
            "label": "Location",
            "fieldname": "location_cf",
            "fieldtype": "Data",
            "width": 150,
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
            "label": "Rejected by Candidate",
            "fieldname": "rejected_by_candidate",
            "width": 190,
        },
        {
            "label": "Selected",
            "fieldname": "selected",
            "width": 145,
        },
        # {
        #     "label": "Total",
        #     "fieldname": "total_count",
        #     "width": 145,
        # },
    ]


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
