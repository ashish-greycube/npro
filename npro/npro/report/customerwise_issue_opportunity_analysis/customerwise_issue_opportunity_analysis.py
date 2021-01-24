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
        dict(label="Customer", fieldname="customer", width=160,),
        dict(label="Issue #", fieldname="issue_count", fieldtype="Int", width=130,),
        dict(label="Opportunity #", fieldname="opp_count", fieldtype="Int", width=130,),
        dict(
            label="Total Opp Amount",
            fieldname="opportunity_amount",
            fieldtype="Currency",
            width=160,
        ),
    ]


def get_conditions(filters):
    where_clause = []
    if filters.get("from_date"):
        where_clause.append("date(iss.creation) >= %(from_date)s")
    if filters.get("to_date"):
        where_clause.append("date(iss.creation) <= %(to_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""


def get_data(filters):

    data = frappe.db.sql(
        """
            select 
                customer, count(iss.name) 'issue_count', 
                count(opp.name) 'opp_count', sum(opp.opportunity_amount) opportunity_amount
            from 
                tabIssue iss
                left outer join tabOpportunity opp on opp.customer_name = iss.customer and opp.status = 'Open' 
            {where_conditions}
            group by 
                iss.customer
        """.format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
        # debug=True,
    )

    return data
