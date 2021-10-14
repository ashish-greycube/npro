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
            select 
                op.name name, op.customer_name, op.modified_by, date(op.modified) modified, 
                COALESCE(pr.stage, cons.stage) sales_stage, 
                COALESCE(pr.requirement, cons.requirement) requirement, 
                comm.content latest_comment
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
            left outer join
            (
                select ROW_NUMBER() over (PARTITION BY reference_name order by creation desc) rn,
                reference_name, content from tabComment
                where reference_doctype = 'Opportunity' and comment_type = 'Comment'
            ) comm on comm.reference_name = op.name and rn = 1            
        {where_conditions}
            order by modified desc
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
            "label": _("Opportunity"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Opportunity",
            "width": 180,
        },
        {
            "label": _("Organization"),
            "fieldname": "customer_name",
            "width": 200,
        },
        {
            "label": _("Requirement"),
            "fieldname": "requirement",
            "width": 200,
        },
        {
            "label": _("Sales Stage"),
            "fieldname": "sales_stage",
            "width": 200,
        },
        {
            "label": _("Last Updated By"),
            "fieldname": "modified_by",
            "width": 100,
        },
        {
            "label": _("Last Update Date"),
            "fieldname": "modified",
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "label": _("Latest Comment"),
            "fieldname": "latest_comment",
            "width": 300,
        },
    ]


def get_conditions(filters):
    where_clause = []
    # where_clause.append("op.status = 'Open'")
    # if filters.get("opportunity_type"):
    #     where_clause.append("op.opportunity_type = %(opportunity_type)s")
    # if filters.get("opportunity_owner"):
    #     where_clause.append("op.opportunity_owner_cf = %(opportunity_owner)s")
    if filters.get("from_date"):
        where_clause.append("op.transaction_date >= %(from_date)s")
    if filters.get("till_date"):
        where_clause.append("op.transaction_date <= %(till_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
