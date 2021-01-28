# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate
import pandas


def execute(filters=None):
    return get_data(filters)


def get_data(filters):
    data = frappe.db.sql(
        """ 
    with fn as
    (
        select
        ld.name, u.full_name owner,
        DATE_FORMAT(LAST_DAY(COALESCE(v.creation, ld.creation)),'%%Y-%%m-%%d') last_changed,
        ROW_NUMBER() over (PARTITION by ld.name order by v.creation DESC) rn,
        v.data 
        from tabLead ld
        left outer join tabUser u on u.name = ld.lead_owner
        left outer join tabVersion v on v.docname = ld.name 
        and v.ref_doctype = 'Lead'
        and v.data REGEXP '.*"changed":.*().*'
        and v.data  REGEXP concat(',\n(   )("',ld.status,'")\n(  ]).*')
        {where_conditions}
    )
    select fn.owner, fn.last_changed, fn.rn
    from fn
    where rn = 1
    """.format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
        # debug=True,
    )

    if not data:
        return [], []

    # add default 0 for all months
    for d in pandas.date_range(
        filters.get("from_date"), filters.get("to_date"), freq="m"
    ):
        data.append(
            {"owner": data[0].owner, "last_changed": d.strftime("%Y-%m-%d"), "rn": 0,}
        )
    print(data)

    df = pandas.DataFrame.from_records(data)
    import numpy as np

    df1 = pandas.pivot_table(
        df,
        index=["owner"],
        values=["rn"],
        columns=["last_changed"],
        aggfunc=sum,
        fill_value=0,
        margins=True,
        dropna=True,
    )

    df1.drop(index="All", axis=0, inplace=True)
    df1.columns = [d for d in df1.columns.to_series().str[1]]
    df2 = df1.reset_index()

    columns = [dict(label="Salesman", fieldname="owner", fieldtype="Data", width=165)]

    columns += [
        dict(
            label=frappe.utils.format_date(col, "MMM YYYY")
            if not col == "All"
            else "Total",
            fieldname=col,
            fieldtype="Int",
            width=95,
        )
        for col in df1.columns
    ]
    return columns, df2.to_dict("r")


def get_conditions(filters):
    conditions = ["ld.status in ('Converted','Do Not Contact')"]
    if filters.get("from_date"):
        conditions += ["ld.creation >= %(from_date)s"]
    if filters.get("to_date"):
        conditions += ["ld.creation <= %(to_date)s"]

    return conditions and " where " + " and ".join(conditions) or ""
