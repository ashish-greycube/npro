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
    select tjo.name job_opening, tjo.job_title, tjo.company, tjo.designation, 
    tjo.customer_cf, 
    tjo.customer_contact_cf, tjo.npro_sourcing_owner_cf, tjo.sales_person_cf,
    appl.no_applied, appl.no_passed_screening, appl.no_selected, 
    appl.no_shared_with_client, appl.no_selected_by_client,
    appl.no_rejected_by_client
    from `tabJob Opening` tjo   
    left outer join (
        select tja.job_title ,
            count(distinct if(tnsl.old_value is NULL,tja.applicant_name,null)) no_applied ,
            count(distinct if(tnsl.new_value ='Accepted',tja.applicant_name,null)) no_selected ,
            count(distinct if(tnsl.new_value ='Client CV Screening',tja.applicant_name,null)) no_shared_with_client ,
            count(distinct if(tnsl.new_value ='Client CV Screening- Accepted',tja.applicant_name,null)) no_selected_by_client ,
            count(distinct if(tnsl.new_value ='Client interview-Rejected',tja.applicant_name,null)) no_rejected_by_client ,
            count(distinct 
                if(tnsl.new_value like '%%CV%%' 
                or tnsl.new_value in ('Rejected', 'Accepted', 'Hold', 'Client Interview'),
                tja.job_title,null)) no_passed_screening 
        from `tabJob Applicant` tja 
        left outer join `tabNPro Status Log` tnsl on tnsl.doc_type = 'Job Applicant'
            and tnsl.docfield_name = 'status' and tnsl.doc_name = tja.name 
        	and date(tnsl.creation) >= %(from_date)s and date(tnsl.creation) <= %(to_date)s
        where date(tja.creation) >= %(from_date)s and date(tja.creation) <= %(to_date)s
        group by tja.job_title 
    ) appl on appl.job_title = tjo.name
    {where_conditions}
""".format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        # debug=True,
    )

    for d in data:
        d["no_passed_screening"] = (
            d.get("no_selected_by_client", 0)
            + d.get("no_rejected_by_client", 0)
            + d.get("no_shared_with_client", 0)
        )
    return data


def get_columns(filters):
    return [
        {
            "label": "Customer",
            "fieldname": "customer_cf",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 145,
        },
        {
            "label": "Customer Contact",
            "fieldname": "customer_contact_cf",
            "fieldtype": "Link",
            "options": "Contact",
            "width": 145,
        },
        {
            "label": "Job Opening",
            "fieldname": "job_opening",
            "fieldtype": "Link",
            "options": "Job Opening",
            "width": 145,
        },
        {
            "label": "NPro Sourcing Owner",
            "fieldname": "npro_sourcing_owner_cf",
            "fieldtype": "Link",
            "options": "User",
            "width": 145,
        },
        {
            "label": "Npro Sales Person",
            "fieldname": "sales_person_cf",
            "fieldtype": "Link",
            "options": "User",
            "width": 145,
        },
        # {
        #     "label": "No Of Vacancies",
        #     "fieldname": "no_of_vacancies_cf",
        #     "width": 145,
        # },
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
            "label": "Client interview-Rejected",
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
