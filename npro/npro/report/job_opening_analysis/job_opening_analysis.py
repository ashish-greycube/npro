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
WITH t1 as
(
		select tja.job_title , tnsl.new_value status, count(tnsl.new_value) ct
        from `tabJob Applicant` tja 
        inner join `tabNPro Status Log` tnsl on tnsl.doc_type = 'Job Applicant'
            and tnsl.docfield_name = 'status' and tnsl.doc_name = tja.name 
            and date(tnsl.creation) >= %(from_date)s and date(tnsl.creation) <= %(to_date)s
        where
            date(tja.creation) >= %(from_date)s and date(tja.creation) <= %(to_date)s
		group by tja.job_title , tnsl.new_value
		order by tja.job_title , tnsl.new_value
) 
select 
	tjo.name job_opening, tjo.job_title, tjo.company, tjo.designation ,
	tjo.customer_cf , tjo.customer_contact_cf , tjo.npro_sourcing_owner_cf , tjo.sales_person_cf ,
	sum(
        case when t1.status in (
        'Screening Call',
        'Screening Call- Rejected',
        'Technical interview',
        'Technical interview- Rejected',
        'Client CV Screening',
        'Client CV Screening- Accepted',
        'Client CV Screening- Rejected',
        'Client Interview',
        'Client interview-Rejected',
        'Client Interview-rescheduled',
        'Client Interview-waiting for feedback',
        'Rejected by candidate',
        'Hold',
        'Accepted'
    ) then 1 else 0 end) cand_applied ,
	sum(case when t1.status in (
        'Technical interview',
        'Technical interview- Rejected',
        'Client CV Screening',
        'Client CV Screening- Accepted',
        'Client CV Screening- Rejected',
        'Client Interview',
        'Client interview-Rejected',
        'Client Interview-rescheduled',
        'Client Interview-waiting for feedback',
        'Rejected by candidate',
        'Hold',
        'Accepted'
    ) then 1 else 0 end) cand_passed_npro_screening ,
	sum(case when t1.status in (
        'Client CV Screening',
        'Client CV Screening- Accepted',
        'Client CV Screening- Rejected',
        'Client Interview',
        'Client interview-Rejected',
        'Client Interview-rescheduled',
        'Client Interview-waiting for feedback',
        'Rejected by candidate',
        'Hold',
        'Accepted'
    ) then 1 else 0 end) no_cv_shared ,
	sum(case when t1.status in (
        'Client CV Screening- Accepted', 
        'Client Interview',
        'Client interview-Rejected', 
        'Client Interview-rescheduled',
        'Client Interview-waiting for feedback',
        'Rejected by candidate',
        'Hold',
        'Accepted'
    ) then 1 else 0 end) cv_accepted_by_client ,
	sum(case when t1.status in ('CV rejected by client') then 1 else 0 end) cv_rejected_by_client ,
    sum(case when t1.status in (
        'Client interview-Rejected', 
        'Client Interview-waiting for feedback' , 
        'Accepted' , 
        'Hold'
    ) then 1 else 0 end) client_interview_held ,
	sum(case when t1.status in ('Client interview-Rejected') then 1 else 0 end) client_interview_rejected ,
	sum(case when t1.status in ('Accepted') then 1 else 0 end) selected 
from `tabJob Opening` tjo 
left outer join t1 on t1.job_title = tjo.name
{where_conditions}
group by 
	job_opening, tjo.job_title, tjo.company, tjo.designation ,
	tjo.customer_cf , tjo.customer_contact_cf , tjo.npro_sourcing_owner_cf , tjo.sales_person_cf 
order by tjo.creation 
""".format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        # debug=True,
    )

    return data


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
            "fieldname": "cand_applied",
            "width": 190,
        },
        {
            "label": "Candidates Passed NPro Screening",
            "fieldname": "cand_passed_npro_screening",
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
