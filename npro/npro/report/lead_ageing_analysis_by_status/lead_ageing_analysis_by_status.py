# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas


def execute(filters=None):
    return get_data(filters)


def build_query(filters):
    sql = """
    select 
        '{label}' age_range, status, count(status) total_count
    from tabLead
        where date(creation) >= '{low}' and date(creation) <= '{high}'
    group by 
        status
    """
    query = []
    start, high, low = 0, filters.get("from_date"), None
    for d in ["range1", "range2", "range3", ""]:
        low = "1900-01-01" if not d else frappe.utils.add_days(high, 0 - filters.get(d))
        label = (
            "{} - {}".format(start, filters.get(d))
            if d
            else "%s +" % filters.get("range3")
        )
        query.append(sql.format(label=label, low=low, high=high))
        # increment counters
        start = 1 + filters.get(d, 0)
        high = frappe.utils.add_days(low, -1)

    return " union all ".join(query)


def get_data(filters):
    # filters = {"from_date":"2021-02-01","range1" : 15, "range2" : 30, "range3": 60 }
    query = build_query(filters)
    data = frappe.db.sql(query, as_dict=True)
    df = pandas.DataFrame.from_records(data)
    df1 = pandas.pivot_table(
        df,
        index=["age_range"],
        values=["total_count"],
        columns=["status"],
        aggfunc=sum,
        fill_value=0,
        margins=True,
    )

    df1.drop(index="All", axis=0, inplace=True)
    df1.columns = [frappe.scrub(d) for d in df1.columns.to_series().str[1]]
    df2 = df1.reset_index()

    columns = [
        dict(label="Ageing Range", fieldname="age_range", fieldtype="Data", width=165)
    ]
    columns += [
        dict(label=frappe.unscrub(col), fieldname=col, fieldtype="Int", width=95)
        for col in df1.columns
    ]
    return columns, df2.to_dict("r")


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions += ["l.creation >= %(from_date)s"]
    if filters.get("to_date"):
        conditions += ["l.creation <= %(to_date)s"]

    return conditions and " where " + " and ".join(conditions) or ""
