# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas


def execute(filters=None):
    return get_data(filters)


def get_data(filters):
    ageing, buckets = get_ageing(filters, "last_updated")
    data = frappe.db.sql(
        """ 
    with fn as
    (
        select
            ld.status, date(COALESCE(v.creation, ld.creation)) last_updated,
            ROW_NUMBER() over (PARTITION by ld.name order by v.creation DESC) rn
        from 
            tabLead ld
            left outer join tabVersion v on v.docname = ld.name 
            and v.ref_doctype = 'Lead'
            and v.data REGEXP '.*"changed":.*().*'
            and v.data  REGEXP concat(',\n(   )("',ld.status,'")\n(  ]).*')
        {where_conditions}
    )
    select 
        fn.status, count(fn.status) total_count, {ageing} ageing
    from 
        fn
    where 
        rn = 1
    group by 
        ageing
    """.format(
            ageing=ageing, where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
    )

    if not data:
        return [], []

    # add a default 0 count for each slab, so report has all slabs
    ageing_defaults = [
        {"ageing": d, "status": data[0].status, "total_count": 0} for d in buckets
    ]
    data += ageing_defaults

    df = pandas.DataFrame.from_records(data)
    import numpy as np

    df1 = pandas.pivot_table(
        df,
        index=["status"],
        columns=["ageing"],
        values=["total_count"],
        aggfunc="sum",
        fill_value=0,
        margins=True,
        dropna=True,
    )
    df1.drop(index="All", axis=0, inplace=True)
    df1.columns = [d for d in df1.columns.to_series().str[1]]
    df2 = df1.reset_index()

    columns = [dict(label="Status", fieldname="status", fieldtype="Data", width=165)]

    columns += [
        dict(label=col, fieldname=col, fieldtype="Int", width=95,)
        for col in df1.columns
    ]
    return columns, df2.to_dict("r")


def get_conditions(filters):
    conditions = ["ld.status in ('New', 'Working','Nurturing')"]
    if filters.get("from_date"):
        conditions += ["date(ld.creation) <= %(from_date)s"]
    if filters.get("till_date"):
        conditions += ["date(ld.creation) >= %(till_date)s"]

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

