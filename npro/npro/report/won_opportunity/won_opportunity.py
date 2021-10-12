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
                op.company,
                op.source,
                op.opportunity_type,
                op.sales_stage,
                op.status,
                op.opportunity_owner_cf,
                op.to_discuss,
                op.contact_person,
                op.opportunity_amount,
                op.transaction_date,
                date(op.contact_date) contact_date
            from 
                tabOpportunity op
            {where_conditions}
        """.format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        debug=True,
    )
    return data or []


def get_columns(filters):
    return [
        {
            "label": _("Organization"),
            "fieldname": "company",
            "width": 200,
        },
        {
            "label": _("Source"),
            "fieldname": "source",
            "width": 200,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "width": 200,
        },
        {
            "label": _("Opportunity Owner"),
            "fieldname": "opportunity_owner",
            "width": 200,
        },
        {
            "label": _("Sales Stage"),
            "fieldname": "sales_stage",
            "width": 200,
        },
        {
            "label": _("Requirement"),
            "fieldname": "requirement",
            "width": 200,
        },
        {
            "label": _("Next Contact Date"),
            "fieldname": "contact_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("To Discuss"),
            "fieldname": "to_discuss",
            "width": 200,
        },
        {
            "label": _("Opp created on"),
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Contact Person"),
            "fieldname": "contact_person",
            "width": 100,
        },
        {
            "label": _("Last Updated By"),
            "fieldname": "updated_by",
            "width": 100,
        },
        {
            "label": _("Last Update Date"),
            "fieldname": "updated_date",
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "label": "Open opportunity amount",
            "fieldname": "open_opportunity_amount",
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "label": "Won opportunity amount",
            "fieldname": "won_opportunity_amount",
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "label": "Lost opportunity amount",
            "fieldname": "lost_opportunity_amount",
            "fieldtype": "Currency",
            "width": 110,
        },
        # Organization,source, status, opportunity owner,sales stage, requirement,
        # next contact date, to discuss, opportunity created on, contact person,
        # last updated by,last update date, latest comment, competitors,
        # open opportunity amount, won opportunity amount, lost opportunity amount,
    ]


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
