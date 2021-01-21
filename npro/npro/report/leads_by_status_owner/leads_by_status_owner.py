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
    df1.columns = [frappe.scrub(d) for d in df1.columns.to_series().str[1]]
    df2 = df1.reset_index()

    columns = [
        dict(label="Sales Rep", fieldname="lead_owner", fieldtype="Data", width=165)
    ]
    columns += [
        dict(label=frappe.unscrub(col), fieldname=col, fieldtype="Int", width=95)
        for col in df1.columns
    ]
    return columns, df2.to_dict("r")


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions += ["date(l.creation) >= %(from_date)s"]
    if filters.get("to_date"):
        conditions += ["date(l.creation) <= %(to_date)s"]

    return conditions and " where " + " and ".join(conditions) or ""
