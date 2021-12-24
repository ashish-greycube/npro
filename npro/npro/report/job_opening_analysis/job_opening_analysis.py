# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe


import frappe
from frappe import _

applicant_status = [
    "Open",
    "Replied",
    "Pending for Internal Screening",
    "CV Shared with Client",
    "CV Selected for Interview",
    "CV Rejected",
    "Interview Scheduled",
    "Rejected",
    "Hold",
    "Accepted",
    "For Future Hire",
]


def execute(filters=None):
    columns, data = [], []
    columns, data = get_columns(filters), get_data(filters)

    return columns, data


def get_data(filters):
    data = frappe.db.sql(
        """
    select tjo.name job_opening, tjo.job_title, tjo.company, tjo.designation, 
    tjo.no_of_vacancies_cf, tjo.customer_cf, 
    tjo.customer_contact_cf, tjo.npro_sourcing_owner_cf, tjo.sales_person_cf,
    appl.no_applied, appl.no_passed_screening, appl.no_selected, 
    appl.no_shared_with_client, appl.no_selected_by_client,
    appl.no_rejected_by_client
    from `tabJob Opening` tjo   
    left outer join (
        select  job_title, 
        count(*) no_applied,
        case 
            when status like 'CV%%' 
            or status in ('Rejected', 'Accepted', 'Hold', 'Interview Scheduled') 
        then 1 else 0 end no_passed_screening,
        sum(if(status='Accepted',1,0)) no_selected,
        sum(if(status='CV Shared with Client',1,0)) no_shared_with_client,
        sum(if(status='CV Selected for Interview',1,0)) no_selected_by_client,
        sum(if(status='CV Rejected',1,0)) no_rejected_by_client
        from `tabJob Applicant` tja 
        group by job_title
    ) appl on appl.job_title = tjo.name
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
            "label": "Customer",
            "fieldname": "customer_cf",
            "width": 145,
        },
        {
            "label": "Customer Contact",
            "fieldname": "customer_contact_cf",
            "width": 145,
        },
        {
            "label": "Job Opening",
            "fieldname": "job_opening",
            "width": 145,
        },
        {
            "label": "NPro Sourcing Owner",
            "fieldname": "npro_sourcing_owner_cf",
            "width": 145,
        },
        {
            "label": "Npro Sales Person",
            "fieldname": "sales_person_cf",
            "width": 145,
        },
        {
            "label": "No Of Vacancies",
            "fieldname": "no_of_vacancies_cf",
            "width": 145,
        },
        {
            "label": "Candidates Applied",
            "fieldname": "no_applied",
            "width": 145,
        },
        {
            "label": "Candidates Passed NPro Screening",
            "fieldname": "no_passed_screening",
            "width": 145,
        },
        {
            "label": "No Of CV Shared",
            "fieldname": "no_shared_with_client",
            "width": 145,
        },
        {
            "label": "CV Selected by Client",
            "fieldname": "no_selected_by_client",
            "width": 145,
        },
        {
            "label": "CV Rejected by Client",
            "fieldname": "no_rejected_by_client",
            "width": 145,
        },
        {
            "label": "Candidates Selected",
            "fieldname": "no_selected",
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
