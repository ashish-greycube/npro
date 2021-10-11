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
            "width": 250,
        },
        {
            "label": _("Lead Name"),
            "fieldname": "lead_name",
            "fieldtype": "Data",
            "width": 250,
        },
        # {
        #     "label": _("Company"),
        #     "fieldname": "company",
        #     "fieldtype": "Link",
        #     "options": "Company",
        #     "width": 250,
        # },
        {
            "label": _("Source"),
            "fieldname": "source",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Next Contact Date"),
            "fieldname": "contact_date",
            # "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Latest Comment"),
            "fieldname": "comment",
            "width": 300,
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
		with fn as (
			select ROW_NUMBER() over (PARTITION BY reference_name order by creation desc) rn,
			reference_name, content from tabComment
			where reference_doctype = 'Lead' 
			and content is not NULL and comment_type = 'Comment'
		)
		SELECT
		ld.name,
		ld.lead_name,
		ld.lead_owner,
		ld.source,
		ld.company,
		date_format(ld.contact_date,'%%d-%%m-%%Y') contact_date,
		fn.content comment
		FROM
			`tabLead` ld 
			left outer join fn on fn.reference_name = ld.name and fn.rn = 1
		WHERE
			company = %(company)s
			AND ld.creation BETWEEN %(from_date)s AND %(to_date)s
			{conditions}
		ORDER BY 
			ld.creation asc """.format(
            conditions=get_conditions(filters)
        ),
        filters,
        as_dict=1,
        # debug=True,
    )


def get_conditions(filters):
    conditions = []
    conditions.append(" and ld.status in ('New', 'Working', 'Nurturing' )")

    return " ".join(conditions) if conditions else ""
