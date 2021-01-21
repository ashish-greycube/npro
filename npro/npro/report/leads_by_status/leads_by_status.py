# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters):
    return frappe.db.sql(
        """
        select
            status, count(status) count
        from
            tabLead
        {where_conditions}
        group by 
            status""".format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
        # debug=True,
    )


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions += ["creation >= %(from_date)s"]
    if filters.get("to_date"):
        conditions += ["creation <= %(to_date)s"]

    return conditions and " where " + " and ".join(conditions) or ""


def get_columns(filters):
    return [
        dict(label="Status", fieldname="status", fieldtype="Data", width=200),
        dict(label="Count", fieldname="count", fieldtype="Int", width=90),
    ]

