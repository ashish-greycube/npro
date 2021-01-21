# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas


def execute(filters=None):
    return get_data(filters)


def get_data(filters):
    # filters = {"from_date":"2021-02-01","range1" : 15, "range2" : 30, "range3": 60 }

    data = frappe.db.sql(
        """ 
    with fn as
    (
        select
        ld.name, ld.status,
        date(COALESCE(v.creation, ld.creation)) last_changed,
        ROW_NUMBER() over (PARTITION by ld.name order by v.creation DESC) rn,
        v.data 
        from tabLead ld
        left outer join tabVersion v on v.docname = ld.name 
        and v.ref_doctype = 'Lead'
        and v.data REGEXP '.*"changed":.*().*'
        and v.data  REGEXP concat(',\n(   )("',ld.status,'")\n(  ]).*')
        {where_conditions} 
    )
    select fn.status, fn.last_changed
    from fn
    where rn = 1
    """.format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
    )
    #
    start, from_date, age_ranges = 0, filters.get("from_date"), []

    for d in ["range1", "range2", "range3"]:
        label = "%s - %s" % (start, filters.get(d))
        days = filters.get(d)
        age_ranges.append((label, days))
        start = filters.get(d, start) + 1
    age_ranges.append(("%s +" % filters.get("range3"), start))

    print(age_ranges)

    for d in data:
        days_diff = frappe.utils.date_diff(from_date, d.last_changed)

        for r in age_ranges:
            if days_diff <= r[1]:
                # print(r, days_diff)
                d.age_range = r[0]
                break
            if not d.age_range:
                d.age_range = age_ranges[-1][0]

    #
    df = pandas.DataFrame.from_records(data)
    import numpy as np

    df1 = pandas.pivot_table(
        df,
        index=["status"],
        columns=["age_range"],
        values=["last_changed"],
        aggfunc="count",
        fill_value=0,
        margins=True,
        dropna=True,
    )
    df1
    df1.drop(index="All", axis=0, inplace=True)
    df1.columns = [frappe.scrub(d) for d in df1.columns.to_series().str[1]]
    df2 = df1.reset_index()
    df2

    columns = [dict(label="Status", fieldname="status", fieldtype="Data", width=165)]

    columns += [
        dict(
            label=col.replace("___", " - ").replace("_+", " +").replace("all", "Total"),
            fieldname=col,
            fieldtype="Int",
            width=95,
        )
        for col in df1.columns
    ]
    return columns, df2.to_dict("r")


def get_conditions(filters):
    conditions = ["ld.status in ('New', 'Working','Nurturing')"]
    if filters.get("from_date"):
        conditions += ["ld.creation <= %(from_date)s"]

    return conditions and " where " + " and ".join(conditions) or ""
