# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, today
import pandas as pd


def execute(filters=None):
    return get_data(filters)


def get_data(filters):
    filters["today"] = today()
    data = frappe.db.sql(
        """
            select 
                tja.status , tjo.customer_cf 
            from tabInterview ti 
            inner join `tabJob Opening` tjo on tjo.name = ti.job_opening 
            inner join `tabJob Applicant` tja on tja.name = ti.job_applicant 
        {where_conditions}
        """.format(
            where_conditions=get_conditions(filters),
        ),
        filters,
    )

    df1 = pd.DataFrame(data, columns=["status", "customer"])
    df2 = df1.pivot_table(index="customer", columns="status", aggfunc=len, fill_value=0)
    columns = [
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "width": 180,
        },
    ] + [dict(label=d, fieldname=d, width=200) for d in df2.columns]

    return columns, df2.reset_index().to_dict(orient="records")


def get_conditions(filters):
    where_clause = []
    where_clause.append("ti.scheduled_on <= %(today)s")

    if filters.get("from_date"):
        where_clause.append("ti.scheduled_on >= %(from_date)s")

    if filters.get("to_date"):
        where_clause.append("ti.scheduled_on <= %(to_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
