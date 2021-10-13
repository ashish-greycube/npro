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
            label="Contact",
            fieldname="name",
            fieldtype="Link",
            options="Contact",
            width=180,
        ),
        dict(
            label="Name",
            fieldname="contact",
            fieldtype="Data",
            width=180,
        ),
        dict(
            label="Designation",
            fieldname="designation",
            fieldtype="Data",
            width=200,
        ),
        dict(
            label="Email",
            fieldname="email_id",
            width=260,
        ),
        dict(
            label="Mobile",
            fieldname="mobile_no",
            width=160,
        ),
        dict(
            label="Reports To",
            fieldname="reports_to_cf",
            fieldtype="Link",
            options="Contact",
            width=260,
        ),
    ]


def get_data(filters):

    data = frappe.db.sql(
        """
        with fn as
        (
            select name, 
            coalesce(email_id,'') email_id, coalesce(mobile_no,'') mobile_no, 
            reports_to_cf, con.designation
            from tabContact con
            where exists
            (
                select 1 from `tabDynamic Link` dl 
                where dl.link_doctype = 'Customer' and dl.parenttype = 'Contact' 
                and dl.parent = con.name and dl.link_name = %(customer)s
            ) 
        ) 
        select fn.name, fn.email_id, fn.mobile_no, fn.designation,
        concat_ws(' ', c.first_name, c.last_name) contact, 
        concat_ws(' ', mgr.first_name, mgr.last_name) reports_to_cf
        from fn 
        inner join tabContact c on c.name = fn.name
        left outer join tabContact mgr on mgr.name = fn.reports_to_cf

              """.format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
        debug=True,
    )

    return data


def get_conditions(filters):
    where_clause = []
    if filters.get("customer"):
        where_clause.append("cus.name = %(customer)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
