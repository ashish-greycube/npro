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
    if filters.get("opportunity_type"):
        where_clause.append("op.opportunity_type = %(opportunity_type)s")
    if filters.get("opportunity_owner"):
        where_clause.append("op.opportunity_owner_cf = %(opportunity_owner)s")
    if filters.get("till_date"):
        where_clause.append("op.transaction_date >= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""


def get_data(filters):
    ageing, buckets = get_ageing(filters, "transaction_date")
    data = frappe.db.sql(
        """
        with fn as 
            (
                select us.full_name opportunity_owner,
                op.opportunity_type, ifnull(op.sales_stage,'UNKNOWN') sales_stage, 
                 op.opportunity_amount, {ageing} ageing
                from `tabOpportunity` op
                left outer join tabUser us on us.name = op.opportunity_owner_cf
                {where_conditions}
            )
        select 
            ageing, sales_stage, count(sales_stage) `count`
        from 
            fn
        group by 
            ageing, sales_stage
        """.format(
            ageing=ageing, where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        debug=True,
    )
    if not data:
        return [], []

    # add a default 0 count for each slab, so report has all slabs
    ageing_defaults = [
        {"ageing": d, "sales_stage": data[0].sales_stage, "count": 0} for d in buckets
    ]
    data += ageing_defaults

    df = pandas.DataFrame.from_records(data)
    df1 = pandas.pivot_table(
        df,
        index=["ageing",],
        values=["count"],
        columns=["sales_stage"],
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
            label="Age of Opportunity", fieldname="ageing", fieldtype="Data", width=130
        ),
    ]

    for col in df1.columns.to_list():
        columns += [
            dict(label=col, fieldname=col, fieldtype="Int", width=150),
        ]

    return columns, df2.to_dict("r")


def get_ageing(filters, age_column):
    ageing = ["case", "else '{} +' end".format(filters.get("range3"))]
    buckets = ["{} +".format(filters.get("range3"))]
    low = 0
    for d in ["range1", "range2", "range3"]:
        days = filters.get(d)
        ageing.insert(
            -1,
            "when `{}` > DATE_SUB(%(from_date)s, INTERVAL {} DAY) then '{} - {}'".format(
                age_column, days + 1, low, days
            ),
        )
        buckets.insert(-1, "{} - {}".format(low, days))
        low = days + 1
    return " \n ".join(ageing), buckets
