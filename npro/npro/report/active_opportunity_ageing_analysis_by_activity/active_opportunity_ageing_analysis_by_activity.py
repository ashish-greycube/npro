# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
import pandas
from pandas.api.types import CategoricalDtype
from operator import itemgetter


def execute(filters=None):
    return get_data(filters)


def get_conditions(filters):
    where_clause = []
    where_clause.append("op.status = 'Open'")
    if filters.get("opportunity_type"):
        where_clause.append("op.opportunity_type = %(opportunity_type)s")
    if filters.get("opportunity_owner"):
        where_clause.append("op.opportunity_owner_cf = %(opportunity_owner)s")
    if filters.get("from_date"):
        where_clause.append("op.transaction_date >= %(from_date)s")
    if filters.get("till_date"):
        where_clause.append("op.transaction_date <= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""


def get_data(filters):
    ageing, buckets = get_ageing(filters, "last_status_updated")
    data = frappe.db.sql(
        """
        with fn as 
            (
                select
                op.sales_stage,
                coalesce(date(ver.creation),op.transaction_date) as 'last_status_updated',
                ROW_NUMBER() OVER (PARTITION BY op.name ORDER BY ver.creation DESC) rn 
                from tabOpportunity op
                left outer join tabUser us on us.name = op.opportunity_owner_cf
                left outer join tabVersion ver on ver.ref_doctype = 'Opportunity' 
                and ver.docname = op.name
                and ver.data REGEXP '.*"changed":.*().*'
                and ver.data REGEXP '.*"sales_stage".*'
                and ver.data  REGEXP concat(',\n(   )("',op.sales_stage,'")\n(  ]).*')
                {where_conditions}               
            )
        select 
            {ageing} ageing, sales_stage, count(sales_stage) `count`
        from 
            fn
        where fn.rn = 1
        group by 
            ageing, sales_stage
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
        {"ageing": d, "sales_stage": data[0].sales_stage, "count": 0} for d in buckets
    ]
    data += ageing_defaults

    df = pandas.DataFrame.from_records(data)
    df1 = pandas.pivot_table(
        df,
        index=[
            "sales_stage",
        ],
        values=["count"],
        columns=["ageing"],
        fill_value=0,
        margins=True,
        margins_name="Total",
        aggfunc=sum,
        dropna=True,
    )
    df1.drop(index="Total", axis=0, inplace=True)
    df1.columns = df1.columns.to_series().str[1]
    df2 = df1.reset_index()

    # sort by sales stage priority_cf
    sales_stages_ordered = get_sales_stage_ordered()
    df2["sales_stage"] = df2["sales_stage"].astype("category")
    df2["sales_stage"].cat.set_categories(sales_stages_ordered, inplace=True)
    df2.sort_values(by="sales_stage", axis=0, inplace=True)

    columns = [
        dict(label="Sales Stage", fieldname="sales_stage", fieldtype="Data", width=130),
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
            "when `{}` > DATE_SUB(%(till_date)s, INTERVAL {} DAY) then '{} - {}'".format(
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
