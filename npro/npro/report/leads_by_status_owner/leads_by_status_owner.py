# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas


def execute(filters=None):
    return get_data(filters)


def get_data(filters):

    columns = [
        dict(label="Sales Rep", fieldname="lead_owner", fieldtype="Data", width=165)
    ]

    data = frappe.db.sql(
        """
        select
            u.full_name lead_owner, l.status, count(l.status) total_count
        from
            tabLead l
            inner join tabUser u on u.name = l.lead_owner
        {where_conditions}
        group by 
            lead_owner, status""".format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
        # debug=True,
    )
    if not data:
        return columns, []

    df = pandas.DataFrame.from_records(data)
    df1 = pandas.pivot_table(
        df,
        index=["lead_owner"],
        values=["total_count"],
        columns=["status"],
        aggfunc=sum,
        fill_value=0,
        margins=True,
    )
    df1.drop(index="All", axis=0, inplace=True)
    df1.columns = [d for d in df1.columns.to_series().str[1]]
    df2 = df1.reset_index()
 
    #  sorting grid columns
    sort_order = (
        frappe.db.get_single_value("NPro Settings", "lead_status_sort_order") or ""
    )
    sort_order = sort_order.split(",")
    columns = columns + sorted([
        dict(label=frappe.unscrub(col), fieldname=col, fieldtype="Int", width=95)
        for col in df1.columns],
        key=lambda x: sort_order.index(x) if x in sort_order
        else 100,
    )

    return columns, df2.to_dict("r")


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions += ["date(l.creation) >= %(from_date)s"]
    if filters.get("to_date"):
        conditions += ["date(l.creation) <= %(to_date)s"]

    return conditions and " where " + " and ".join(conditions) or ""
