# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
import pandas as pd
import numpy as np


def execute(filters=None):
    return get_data(filters)


def get_data(filters):
    columns = get_columns(filters)

    data = frappe.db.sql(
        """
        select 
            tja.name applicant, tja.applicant_name, tja.source, 
            tja.status, tjo.job_title, tjo.customer_cf,
            concat_ws(' - ', round(tja.lower_range), round(tja.upper_range)) salary_range,
            tja.applicant_total_experience_cf, tja.previous_company_cf
        from `tabJob Applicant` tja 
        inner join `tabJob Opening` tjo on tjo.name = tja.job_title 
    """,
        as_dict=True,
    )
    df1 = pd.DataFrame.from_records(data)
    df1.set_index("applicant")

    social_media = frappe.db.sql(
        """
    select 
        tja.name applicant, tsmpu.social_media_platform, 
        coalesce(tsmpu.profile_url,"") profile_url 
    from `tabSocial Media Profile URL` tsmpu 
    inner join `tabJob Applicant` tja on tja.name = tsmpu.parent ; 
    """,
        as_dict=True,
    )

    if not social_media:
        return columns, df1.to_dict(orient="records")

    df2 = pd.DataFrame.from_records(social_media)
    df2 = pd.pivot_table(
        df2,
        index=["applicant"],
        columns=["social_media_platform"],
        values=["profile_url"],
        aggfunc="first",
        fill_value="",
    )
    df2.columns = [
        frappe.scrub(d.replace("profile_url_", "")) for d in df2.columns.map("_".join)
    ]
    df3 = pd.merge(df1, df2, how="left", on=["applicant"]).replace(
        np.nan, "", regex=True
    )

    social_media_columns = [
        dict(label=frappe.unscrub(d), fieldname=d, width=150) for d in df2.columns
    ]

    columns[5:5] = social_media_columns

    return columns, df3.to_dict(orient="records")


def get_columns(filters):
    return [
        {
            "label": _("Applicant Name"),
            "fieldname": "applicant_name",
            "width": 180,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "width": 120,
        },
        {
            "label": _("Customer"),
            "fieldname": "customer_cf",
            "width": 220,
        },
        {
            "label": _("Source"),
            "fieldname": "source",
            "width": 180,
        },
        {
            "label": _("Technology"),
            "fieldname": "job_title",
            "width": 200,
        },
        {
            "label": _("City"),
            "fieldname": "city",
            "width": 200,
        },
        {
            "label": _("Total Experience"),
            "fieldname": "applicant_total_experience_cf",
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "label": _("Previous Company"),
            "fieldname": "previous_company_cf",
            "width": 150,
        },
        {
            "label": _("Expected Salary Range"),
            "fieldname": "salary_range",
            "width": 180,
        },
    ]


def get_conditions(filters):
    where_clause = []
    # if filters.get("from_date"):
    #     where_clause.append("op.transaction_date >= %(from_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
