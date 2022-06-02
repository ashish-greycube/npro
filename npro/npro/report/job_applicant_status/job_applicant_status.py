# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)

    return columns, data


def get_data(filters):
    data = frappe.db.sql(
        """
    select 
        tja.name applicant, tja.applicant_name , tja.phone_number , tja.job_title , 
        tja.job_title_cf , tja.status , tja.customer_cf , tr.rejected_reason 
    from `tabJob Applicant` tja 
    left outer join (
        select parent, GROUP_CONCAT(rejected_reason) rejected_reason
        from `tabNpro Rejected Reason Detail` tnrrd
        group by parent
    ) tr on tr.parent = tja.name
""".format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=1,
        debug=True,
    )

    return data


def get_columns(filters):
    return csv_to_columns(
        """
Job Opening ID,job_title,Link,Job Opening,150
Applicant Name,applicant_name,,,230
Mobile number,phone_number,,,145
Job title,job_title_cf,,,250
Customer,customer_cf,Link,Customer,175
Status,status,,,230
Rejected reason,rejected_reason,,,500
        """
    )


def csv_to_columns(csv_str):
    props = ["label", "fieldname", "fieldtype", "options", "width"]
    return [
        zip(props, [x.strip() for x in col.split(",")])
        for col in csv_str.split("\n")
        if col.strip()
    ]


def get_conditions(filters):
    where_clause = []
    if filters.get("interviewer"):
        where_clause.append("tif.interviewer = %(interviewer)s")
    return " where " + " and ".join(where_clause) if where_clause else ""
