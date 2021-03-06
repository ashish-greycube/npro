# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas


def execute(filters=None):
    return get_data(filters)


def get_data(filters):
    ageing, buckets = get_ageing(filters, "ld.creation")
    data = frappe.db.sql(
        """
        select 
            u.full_name lead_owner, {ageing} ageing, count(ld.status) total_count
        from 
            tabLead ld
            inner join tabUser u on u.name = ld.lead_owner
            {where_conditions}
        group by 
            u.full_name, ageing
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
        {"ageing": d, "lead_owner": data[0].lead_owner, "total_count": 0}
        for d in buckets
    ]
    data += ageing_defaults

    df = pandas.DataFrame.from_records(data)
    df1 = pandas.pivot_table(
        df,
        index=["lead_owner"],
        values=["total_count"],
        columns=["ageing"],
        aggfunc=sum,
        fill_value=0,
        margins=True,
    )

    df1.drop(index="All", axis=0, inplace=True)
    df1.columns = [d for d in df1.columns.to_series().str[1]]
    df2 = df1.reset_index()

    columns = [
        dict(label="Sales Rep", fieldname="lead_owner", fieldtype="Data", width=165)
    ]

    columns += [
        dict(
            label=col,
            fieldname=col,
            fieldtype="Int",
            width=95,
        )
        for col in df1.columns
    ]
    return columns, df2.to_dict("r")


def get_conditions(filters):
    conditions = []
    lead_active_status = (
        frappe.db.get_single_value("NPro Settings", "lead_active_status") or ""
    )
    conditions += [
        "status in ({})".format(
            ",".join("'{}'".format(d) for d in lead_active_status.split(","))
        )
    ]

    if filters.get("from_date"):
        conditions += ["date(ld.creation) >= %(from_date)s"]
    if filters.get("till_date"):
        conditions += ["date(ld.creation) <= %(till_date)s"]

    return conditions and " where " + " and ".join(conditions) or ""


def get_ageing(filters, age_column):
    ageing = ["case", "else '{} +' end".format(filters.get("range3"))]
    buckets = ["{} +".format(filters.get("range3"))]
    low = 0
    for d in ["range1", "range2", "range3"]:
        days = filters.get(d)
        ageing.insert(
            -1,
            "when date({}) > DATE_SUB(%(till_date)s, INTERVAL {} DAY) then '{} - {}'".format(
                age_column, days + 1, low, days
            ),
        )
        buckets.insert(-1, "{} - {}".format(low, days))
        low = days + 1
    return " \n ".join(ageing), buckets


def get_sales_stage_ordered():
    return [
        d[0]
        for d in frappe.db.get_all("Sales Stage", as_list=True, order_by="priority_cf")
    ]
