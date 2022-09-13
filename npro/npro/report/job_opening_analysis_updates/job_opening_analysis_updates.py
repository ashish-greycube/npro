# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
import pandas
from frappe import _
from frappe.utils import cint


def execute(filters=None):
    columns, data = [], []
    columns, data = get_columns(filters), get_data(filters)

    return columns, data


def get_data(filters):
    filters["from_date"] = filters.get("from_date") or "1900-01-01"
    filters["to_date"] = filters.get("to_date") or "2900-01-01"

    if cint(filters.get("ignore_duration")):
        filters["from_date"] = "1900-01-01"
        filters["to_date"] = "2500-01-01"

    data = frappe.db.sql(
        """
		select 
			tjo.name job_opening, tjo.job_title, tjo.company, tjo.designation , tjo.location_cf ,
			tjo.customer_cf , tjo.customer_contact_cf , tjo.npro_sourcing_owner_cf , tjo.sales_person_cf ,
			tjo.status
		from `tabJob Opening` tjo 
		{where_conditions}
		order by tjo.creation """.format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
    )

    npro_technical_interview_passed = {}
    for d in frappe.db.sql(
        """
    select 
        job_opening , count(job_applicant) ct  
        from tabInterview ti 
        where ti.status = 'Cleared'
        and ti.scheduled_on between %(from_date)s and %(to_date)s
        and ti.modified between %(from_date)s and %(to_date)s
        and exists (select 1 from `tabInterview Round` x 
        where x.name = ti.interview_round 
        and x.interview_type in ('Internal technical interview','Technical interview'))
        group by job_opening 
    """,
        filters,
        as_dict=True,
    ):
        npro_technical_interview_passed[d.job_opening] = d.ct

    status_data = frappe.db.sql(
        """
		select 
		tja.job_title , new_value , count(new_value) ct 
		from `tabNPro Status Log` tnsl 
		inner join `tabJob Applicant` tja on tja.name = tnsl.doc_name and tnsl.doc_type = 'Job Applicant'
		where date(tnsl.modified) >= %(from_date)s and date(tnsl.modified) <= %(to_date)s 
		group by tja.job_title , new_value 
	""",
        filters,
        as_dict=True,
    )
    status_wise_counts = {}

    if status_data:
        df = pandas.DataFrame.from_records(status_data)
        df1 = pandas.pivot_table(
            df,
            index=["job_title"],
            columns=["new_value"],
            aggfunc=sum,
            fill_value=0,
            dropna=True,
        )
        df1.columns = df1.columns.to_series().str[1]
        df2 = df1.reset_index()
        for d in df2.to_dict("r"):
            status_wise_counts[d["job_title"]] = d

    for d in data:
        d["total"] = 0
        d["npro_technical_interview_passed"] = npro_technical_interview_passed.get(
            d.job_opening, 0
        )
        for col, statuses in STATUS_MAP.items():
            for status in statuses:
                d[col] = d.get(col, 0) + status_wise_counts.get(d.job_opening, {}).get(
                    status, 0
                )
            d[col] = d.get(col) or None
            d["total"] = d["total"] + cint(d[col])

    if not cint(filters.get("ignore_duration")):
        data = [d for d in data if d.get("total")]

    return data


def get_conditions(filters):
    where_clause = []
    if filters.get("job_opening"):
        where_clause.append("tjo.name = %(job_opening)s")
    if filters.get("customer"):
        where_clause.append("tjo.customer_cf = %(customer)s")

    return " where " + " and ".join(where_clause) if where_clause else ""


def get_columns(filters):
    return csv_to_columns(
        """
		Customer,customer_cf,Link,Customer,190
		Customer Contact,customer_contact_cf,Link,Contact,190
		Job Opening,job_opening,Link,Job Opening,120
		Job Title,job_title,Data,230
		Location,location_cf,Data,150
		NPro Sourcing Owner,npro_sourcing_owner_cf,Link,User,190
		Npro Sales Person,sales_person_cf,Link,User,190
		Candidates Applied,applied,Int,190
		Candidates Passed NPro Screening,npro_screening_passed,Int,275
		Candidate passed Npro technical interview,npro_technical_interview_passed,Int,290
		No Of CV Shared,cv_shared,Int,190
		CV Accepted by Client,cv_accepted_by_client,Int,190
		CV Rejected by Client,cv_rejected_by_client,Int,190
		Client Interview held,client_interview_held,Int,190
		Client interview-Rejected,client_interview_rejected,int,190
		Rejected by Candidate,rejected_by_candidate,Int,180
		Selected,selected,Int,145
		"""
    )


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


def csv_to_columns(csv_str):
    props = ["label", "fieldname", "fieldtype", "options", "width"]
    return [
        zip(props, [x.strip() for x in col.split(",")])
        for col in csv_str.split("\n")
        if col.strip()
    ]


STATUS_MAP = {
    "applied": ["Screening Call", "Screening Call - Rejected"],
    "npro_screening_passed": [
        "Technical interview",
        "Technical interview- Rejected",
    ],
    "npro_technical_interview_passed": [
        "Technical interview",
        "Technical interview- Rejected",
    ],
    "cv_shared": [
        "Client CV Screening",
    ],
    "cv_accepted_by_client": [
        "Client CV Screening- Accepted",
        "Client Interview",
    ],
    "cv_rejected_by_client": ["Client CV Screening- Rejected"],
    "client_interview_held": [
        "Client interview-Rejected",
        "Client Interview-waiting for feedback",
        "Accepted",
        "Hold",
    ],
    "client_interview_rejected": ["Client interview-Rejected"],
    "rejected_by_candidate": ["Rejected by Candidate"],
    "selected": ["Accepted"],
}
