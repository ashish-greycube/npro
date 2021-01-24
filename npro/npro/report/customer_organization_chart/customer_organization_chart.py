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
            fieldtype="Link",
            options="Customer",
            width=160,
        ),
        dict(
            label="L1 Contact",
            fieldname="l1_name",
            fieldtype="Link",
            options="Contact",
            width=160,
        ),
        dict(label="L1 Communication", fieldname="l1_comm", width=160,),
        dict(
            label="L2 Contact",
            fieldname="l2_name",
            fieldtype="Link",
            options="Contact",
            width=160,
        ),
        dict(label="L2 Communication", fieldname="l2_comm", width=160,),
        dict(
            label="L3 Contact",
            fieldname="l3_name",
            fieldtype="Link",
            options="Contact",
            width=160,
        ),
        dict(label="L3 Communication", fieldname="l3_comm", width=160,),
    ]


def get_data(filters):

    data = frappe.db.sql(
        """
            with l1 as
            (
                select name l1_name, concat_ws(' ',email_id, mobile_no) l1_comm 
                from tabContact
                where reports_to_cf is null
            ),
            l2 as 
            (
                select l1_name, l1_comm, x.name l2_name, concat_ws(' ',email_id, mobile_no) l2_comm
                from l1
                left outer join tabContact x on x.reports_to_cf = l1_name
            ),
            fn_contact as
            (
                select l1_name, l1_comm, l2_name, l2_comm, x.name l3_name, concat_ws(' ',email_id, mobile_no) l3_comm
                from l2
                left outer join tabContact x on x.reports_to_cf = l2.l2_name
            )
            select 
                cus.name customer, fn_contact.*
            from tabCustomer cus
                left outer join `tabDynamic Link` dl on dl.link_name = cus.name 
                and dl.link_doctype = 'Customer' and dl.parenttype = 'Contact'
                left outer join fn_contact on dl.parent in (l1_name, l2_name, l3_name) 
            {where_conditions}
            order by 
                ifnull(customer,'zzz')
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

