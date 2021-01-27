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
            label="Customer",
            fieldname="customer",
            width=160,
        ),
        dict(
            label="Issue #",
            fieldname="issue_count",
            fieldtype="Int",
            width=130,
        ),
        dict(
            label="Opportunity #",
            fieldname="opp_count",
            fieldtype="Int",
            width=130,
        ),
        dict(
            label="Total Opp Amount",
            fieldname="opportunity_amount",
            fieldtype="Currency",
            width=160,
        ),
    ]


def get_issue_conditions(filters):
    where_clause = []
    if filters.get("from_date"):
        where_clause.append("date(iss.creation) >= %(from_date)s")
    if filters.get("to_date"):
        where_clause.append("date(iss.creation) <= %(to_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""


def get_opportunity_conditions(filters):
    where_clause = []
    where_clause.append("status = 'Open'")
    if filters.get("from_date"):
        where_clause.append("date(transaction_date) >= %(from_date)s")
    if filters.get("to_date"):
        where_clause.append("date(transaction_date) <= %(to_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""


def get_data(filters):

    data = frappe.db.sql(
        """
            select 
                t.customer, 
                sum(t.issue_count) issue_count, 
                sum(t.opp_count) opp_count,
                sum(t.opportunity_amount) opportunity_amount
            from             
            (
                select 
                    customer, count(iss.name) 'issue_count', 
                    0 'opp_count', 0 opportunity_amount
                from 
                    tabIssue iss
                    {where_issue}
                group by 
                    iss.customer
                union all                
                select 
                    opp.customer_name, 0 'issue_count', 
                    count(opp.name) 'opp_count', sum(opp.opportunity_amount) opportunity_amount
                from 
                    tabOpportunity opp
                    {where_opportunity}
                group by 
                    opp.customer_name
            ) t
            group by 
                t.customer 
        """.format(
            where_issue=get_issue_conditions(filters),
            where_opportunity=get_opportunity_conditions(filters),
        ),
        filters,
        as_dict=True,
        # debug=True,
    )

    return data
