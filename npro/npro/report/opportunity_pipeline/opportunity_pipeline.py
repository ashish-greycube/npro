# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
import pandas
from operator import itemgetter


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_columns(filters):
    return [
        dict(
            label="Opportunity Type",
            fieldname="opportunity_type",
            width=160,
        ),
        dict(
            label="Opportunity Owner",
            fieldname="opportunity_owner",
            width=160,
        ),
        dict(
            label="Sales Stage",
            fieldname="sales_stage",
            width=160,
        ),
        dict(
            label="Count #",
            fieldname="count",
            fieldtype="Int",
            width=100,
        ),
        dict(
            label="Amount (SAR)",
            fieldname="amount",
            fieldtype="Currency",
            width=100,
        ),
    ]


def get_conditions(filters):
    where_clause = []

    if filters.get("from_date"):
        where_clause.append("op.transaction_date >= %(from_date)s")
    if filters.get("to_date"):
        where_clause.append("op.transaction_date <= %(to_date)s")
    if filters.get("opportunity_type"):
        where_clause.append("op.opportunity_type = %(opportunity_type)s")
    if filters.get("opportunity_owner"):
        where_clause.append("op.opportunity_owner_cf = %(opportunity_owner)s")

    return " where " + " and ".join(where_clause) if where_clause else ""


def get_data(filters):

    data = frappe.db.sql(
        """
        with fn as 
            (
                select us.full_name opportunity_owner,
                op.opportunity_type, ifnull(op.sales_stage,'UNKNOWN') sales_stage, 
                coalesce(stg.priority_cf,-1) priority,
                op.opportunity_amount
                from `tabOpportunity` op
                left outer join `tabSales Stage` stg on stg.name = op.sales_stage 
                left outer join tabUser us on us.name = op.opportunity_owner_cf
                {where_conditions}
            )
        select 
            opportunity_type, opportunity_owner, sales_stage, priority, 
            count(sales_stage) `count`, sum(opportunity_amount) amount
        from 
            fn
        group by 
            opportunity_type, opportunity_owner, sales_stage, priority
        order by
            opportunity_type, opportunity_owner, sales_stage, priority
        """.format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
        # debug=True,
    )

    return data
