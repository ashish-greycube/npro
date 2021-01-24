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
        dict(label="Customer", fieldname="customer_name", width=160,),
        dict(label="Title", fieldname="title", width=160,),
        dict(label="Opp Type", fieldname="opportunity_type", width=110,),
        dict(
            label="Creation Date",
            fieldname="transaction_date",
            fieldtype="Date",
            width=100,
        ),
        dict(
            label="Last Updated",
            fieldname="last_status_updated",
            fieldtype="Date",
            width=100,
        ),
        dict(label="Close Date", fieldname="close_date", fieldtype="Date", width=100,),
        dict(
            label="Amount",
            fieldname="opportunity_amount",
            fieldtype="Currency",
            width=110,
        ),
        dict(
            label="Opportunity",
            fieldname="name",
            fieldtype="Link",
            options="Opportunity",
            width=160,
        ),
        dict(label="Owner", fieldname="opportunity_owner_cf", width=160,),
    ]


def get_conditions(filters):
    where_clause = []
    if filters.get("opportunity_status"):
        where_clause.append("op.status = %(opportunity_status)s")
    if filters.get("from_date"):
        where_clause.append("op.transaction_date >= %(from_date)s")
    if filters.get("to_date"):
        where_clause.append("op.transaction_date <= %(to_date)s")
    if filters.get("opportunity_owner"):
        where_clause.append("op.opportunity_owner_cf = %(opportunity_owner)s")
    if filters.get("opportunity_type"):
        where_clause.append("op.opportunity_type = %(opportunity_type)s")

    return " where " + " and ".join(where_clause) if where_clause else ""


def get_data(filters):

    data = frappe.db.sql(
        """
            with fn as 
            (
                select
                op.customer_name, op.title, op.opportunity_type,
                op.opportunity_owner_cf, op.transaction_date,
                date(ver.creation) as 'last_status_updated',
                case 
                when op.sales_stage in ('Closed', 'Converted', 'Lost') 
                then date(ver.creation) else NULL end 'close_date',
                op.opportunity_amount, op.name
                , ROW_NUMBER() OVER (PARTITION BY op.name ORDER BY ver.creation DESC) rn 
            from 
                tabOpportunity op
            left outer join 
                tabVersion ver on ver.ref_doctype = 'Opportunity' 
                and ver.docname = op.name
                and ver.data REGEXP '.*"changed":.*().*'
                and ver.data REGEXP '.*"sales_stage".*'
                and ver.data  REGEXP concat(',\n(   )("',op.sales_stage,'")\n(  ]).*')
            {where_conditions}
            )
            select * 
                from fn
            where
                fn.rn = 1
        """.format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
        # debug=True,
    )

    return data
