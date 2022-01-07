# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
import pandas
from operator import itemgetter


def execute(filters=None):
    return get_data(filters)


def get_conditions(filters):
    where_clause = []
    where_clause.append("tjo.status = 'Open'")
    if filters.get("customer_cf"):
        where_clause.append("tjo.customer_cf = %(customer_cf)s")
    if filters.get("npro_sourcing_owner"):
        where_clause.append("tjo.npro_sourcing_owner_cf = %(npro_sourcing_owner)s")
    if filters.get("from_date"):
        where_clause.append("tjo.creation >= %(from_date)s")
    if filters.get("till_date"):
        where_clause.append("tjo.creation <= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""


def get_data(filters):
    ageing, buckets = get_ageing(filters, "creation")
    print(ageing)
    data = frappe.db.sql(
        """
        with fn as 
            (
                select coalesce(tjo.customer_cf,'') customer_cf, {ageing} ageing
                from `tabJob Opening` tjo
                {where_conditions}
            )
        select 
            ageing, customer_cf, count(customer_cf) `count`
        from 
            fn
        group by 
            ageing, customer_cf
        """.format(
            ageing=ageing,
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        # debug=True,
    )
    if not data:
        return [], []

    # add a default 0 count for each slab, so report has all slabs
    ageing_defaults = [
        {"ageing": d, "customer_cf": data[0].customer_cf, "count": 0} for d in buckets
    ]
    data += ageing_defaults

    df = pandas.DataFrame.from_records(data)
    df1 = pandas.pivot_table(
        df,
        index=[
            "customer_cf",
        ],
        values=["count"],
        columns=["ageing"],
        fill_value=0,
        margins=True,
        margins_name="Total",
        aggfunc=sum,
        dropna=True,
    )
    df1.drop(index="Total", axis=0, inplace=True)
    df1.columns = df1.columns.to_series().str[1]
    df2 = df1.reset_index()

    columns = [
        dict(
            label="Customer",
            fieldname="customer_cf",
            fieldtype="Link",
            options="Customer",
            width=130,
        ),
    ]

    for col in df1.columns:
        columns += [
            dict(label=col, fieldname=col, fieldtype="Int", width=150),
        ]

    out = df2.to_dict("records")
    return columns, sort_data(out)


def get_ageing(filters, age_column):
    ageing = ["case", "else '{} +' end".format(filters.get("range3"))]
    buckets = ["{} +".format(filters.get("range3"))]
    low = 0
    for d in ["range1", "range2", "range3"]:
        days = filters.get(d)
        ageing.insert(
            -1,
            "when `{}` > DATE_SUB(%(till_date)s, INTERVAL {} DAY) then '{} - {}'".format(
                age_column, days + 1, low, days
            ),
        )
        buckets.insert(-1, "{} - {}".format(low, days))
        low = days + 1
    return " \n ".join(ageing), buckets


def sort_data(lst):
    # row_order = [
    #     d[0]
    #     for d in frappe.db.get_all("Sales Stage", as_list=True, order_by="priority_cf")
    # ]

    # return sorted(
    #     lst,
    #     key=lambda x: row_order.index(x["sales_stage"])
    #     if x["sales_stage"] in row_order
    #     else 100,
    # )
    return lst
