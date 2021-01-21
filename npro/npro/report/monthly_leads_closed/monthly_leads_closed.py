# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas


def execute(filters=None):
    return get_data(filters)


def get_data(filters):
    data = frappe.db.sql(
        """ 
    with fn as
    (
        select
        ld.name, ld.status,
        DATE_FORMAT(COALESCE(v.creation, ld.creation),'%%b-%%Y') last_changed,
        ROW_NUMBER() over (PARTITION by ld.name order by v.creation DESC) rn,
        v.data 
        from tabLead ld
        left outer join tabVersion v on v.docname = ld.name 
        and v.ref_doctype = 'Lead'
        and v.data REGEXP '.*"changed":.*().*'
        and v.data  REGEXP concat(',\n(   )("',ld.status,'")\n(  ]).*')
        {where_conditions}
    )
    select fn.status, fn.last_changed, fn.rn
    from fn
    where rn = 1
    """.format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
        debug=True,
    )

    if not data:
        return [], []

    #
    df = pandas.DataFrame.from_records(data)
    import numpy as np

    df1 = pandas.pivot_table(
        df,
        index=["status"],
        values=["rn"],
        columns=["last_changed"],
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
            label=frappe.unscrub(
                col.replace("___", " - ").replace("_+", " +").replace("all", "Total")
            ),
            fieldname=col,
            fieldtype="Int",
            width=95,
        )
        for col in df1.columns
    ]
    return columns, df2.to_dict("r")


def get_conditions(filters):
    conditions = ["ld.status in ('Qualified', 'Unqualified','Converted')"]
    if filters.get("from_date"):
        conditions += ["ld.creation >= %(from_date)s"]
    if filters.get("to_date"):
        conditions += ["ld.creation <= %(to_date)s"]

    return conditions and " where " + " and ".join(conditions) or ""
