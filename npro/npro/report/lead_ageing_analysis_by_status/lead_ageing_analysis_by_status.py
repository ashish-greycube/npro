# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas


def execute(filters=None):
    return get_data(filters)


def get_data(filters):
    ageing, _ = get_ageing(filters, "creation")

    data = frappe.db.sql(
        """
    with fn as
    (
        select 
            status, {ageing} ageing
        from 
            tabLead
        {where_conditions}
    )
    select 
        fn.ageing, fn.status, count(fn.status) total_count
    from 
        fn
    group by 
        fn.ageing, fn.status
    """.format(
            ageing=ageing, where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        # debug=True,
    )
    df = pandas.DataFrame.from_records(data)
    df1 = pandas.pivot_table(
        df,
        index=["ageing"],
        values=["total_count"],
        columns=["status"],
        aggfunc=sum,
        fill_value=0,
        margins=True,
    )

    df1.drop(index="All", axis=0, inplace=True)
    df1.columns = [frappe.scrub(d) for d in df1.columns.to_series().str[1]]
    df2 = df1.reset_index()

    columns = [dict(label="Age", fieldname="ageing", fieldtype="Data", width=165)]
    columns += [
        dict(label=frappe.unscrub(col), fieldname=col, fieldtype="Int", width=95)
        for col in df1.columns
    ]
    return columns, df2.to_dict("r")


def get_conditions(filters):
    conditions = []
    if filters.get("till_date"):
        conditions += ["date(creation) >= %(till_date)s"]
    if filters.get("from_date"):
        conditions += ["date(creation) <= %(from_date)s"]

    return conditions and " where " + " and ".join(conditions) or ""


def get_ageing(filters, age_column):
    ageing = ["case", "else '{} +' end".format(filters.get("range3"))]
    buckets = ["{} +".format(filters.get("range3"))]
    low = 0
    for d in ["range1", "range2", "range3"]:
        days = filters.get(d)
        ageing.insert(
            -1,
            "when date(`{}`) > DATE_SUB(%(from_date)s, INTERVAL {} DAY) then '{} - {}'".format(
                age_column, days + 1, low, days
            ),
        )
        buckets.insert(-1, "{} - {}".format(low, days))
        low = days + 1
    return " \n ".join(ageing), buckets

