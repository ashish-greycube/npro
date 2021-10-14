# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters):
    data = frappe.db.sql(
        """
        with fn as
        (   
            select 
                op.opportunity_owner_cf, coalesce(pr.stage, cons.stage) stage
            from 
                tabOpportunity op     
            left outer join 
            (
                select parent, stage, project_name requirement, opportunity_close_date
                from `tabOpportunity Project Detail CT`
            ) pr on pr.parent = op.name and op.opportunity_type = 'Project'
            left outer join 
            (
                select parent, stage, project_name requirement, opportunity_close_date
                from `tabOpportunity Consulting Detail CT`
            ) cons on cons.parent = op.name and op.opportunity_type = 'Consulting'
            {where_conditions}
        )
        select fn.opportunity_owner_cf, 
        sum(case when stage not in ('Won','Lost') then 1 else 0 end) open_count,
        sum(case when stage in ('Won') then 1 else 0 end) won_count,
        count(stage) total_count,
        100 * sum(case when stage in ('Won') then 1 else 0 end)  / count(stage)  efficiency
        from fn
        group by fn.opportunity_owner_cf
        order by fn.opportunity_owner_cf

        """.format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        # debug=True,
    )
    return data or []


def get_columns(filters):
    return [
        {
            "label": _("Opportunity Owner"),
            "fieldname": "opportunity_owner_cf",
            "width": 200,
        },
        {
            "label": _("Total Opportunity Count"),
            "fieldname": "total_count",
            "fieldtype": "Int",
            "width": 220,
        },
        {
            "label": _("Open Requirement Count"),
            "fieldname": "open_count",
            "fieldtype": "Int",
            "width": 220,
        },
        {
            "label": _("Won Requirement Count"),
            "fieldname": "won_count",
            "fieldtype": "Int",
            "width": 220,
        },
        {
            "label": _("Efficiency"),
            "fieldname": "efficiency",
            "fieldtype": "Percent",
            "width": 120,
        },
    ]


def get_conditions(filters):
    where_clause = []
    # where_clause.append("op.status = 'Open'")
    if filters.get("from_date"):
        where_clause.append("op.transaction_date >= %(from_date)s")
    if filters.get("till_date"):
        where_clause.append("op.transaction_date <= %(till_date)s")
    if filters.get("organization"):
        where_clause.append("op.customer_name <= %(organization)s")

    return " where " + " and ".join(where_clause) if where_clause else ""


@frappe.whitelist()
def get_organizations():
    data = frappe.db.sql(
        """
        select distinct customer_name from tabOpportunity
        order by customer_name
    """
    )
    return "\n".join([d[0] for d in data])
