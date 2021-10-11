# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _
import frappe


def execute(filters={}):
    filters["status"] = "Opportunity"
    columns, data = get_columns(), get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": _("Lead"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Lead",
            "width": 180,
        },
        {
            "fieldname": "lead_owner",
            "label": _("Lead Owner"),
            "fieldtype": "Link",
            "options": "User",
            "width": 180,
        },
        {
            "label": _("Lead Name"),
            "fieldname": "lead_name",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": _("Company"),
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 180,
        },
        {
            "label": _("Source"),
            "fieldname": "source",
            "fieldtype": "Data",
            "width": 180,
        },
        # {
        #     "label": _("Owner"),
        #     "fieldname": "owner",
        #     "fieldtype": "Link",
        #     "options": "user",
        #     "width": 120,
        # },
    ]
    return columns


def get_data(filters):
    return frappe.db.sql(
        """
		SELECT
			`tabLead`.name,
			`tabLead`.lead_name,
			`tabLead`.lead_owner,
			`tabLead`.source,
			`tabLead`.company
		FROM
			`tabLead` 
		WHERE
			company = %(company)s
			AND `tabLead`.creation BETWEEN %(from_date)s AND %(to_date)s
			{conditions}
		ORDER BY 
			`tabLead`.creation asc """.format(
            conditions=get_conditions(filters)
        ),
        filters,
        as_dict=1,
        debug=True,
    )


def get_conditions(filters):
    conditions = []

    if filters.get("status"):
        conditions.append(" and `tabLead`.status=%(status)s")

    return " ".join(conditions) if conditions else ""
