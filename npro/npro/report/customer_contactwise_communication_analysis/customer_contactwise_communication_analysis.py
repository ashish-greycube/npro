# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
import pandas
from operator import itemgetter


def execute(filters=None):
    return get_data(filters)


def get_conditions(filters):
    where_clause = []
    if filters.get("from_date"):
        where_clause += ["date(comm.creation) >= %(from_date)s"]
    if filters.get("to_date"):
        where_clause += ["date(comm.creation) <= %(to_date)s"]
    if filters.get("communication_medium"):
        where_clause += ["comm.communication_medium = %(communication_medium)s"]

    return " where " + " and ".join(where_clause) if where_clause else ""


def get_data(filters):
    filters.today = frappe.utils.getdate()
    data = frappe.db.sql(
        """
        with fn as
        (
            select
                dl.link_name customer, cml.link_name contact, 
                datediff(%(today)s,communication_date) days_since_last_communication, communication_medium
            from 
                tabCommunication comm
                inner join `tabCommunication Link` cml on cml.parent = comm.name 
                and cml.link_doctype = 'Contact'
                left outer join `tabDynamic Link` dl on dl.link_doctype = 'Customer' 
                and dl.parenttype = 'Contact'
                and dl.parent = cml.link_name 
            {where_conditions}
                and not exists (
                 select 1 from tabEvent e
                 where comm.reference_doctype = 'Event' 
                 and e.name = comm.reference_name and e.status = 'Open'
             )
        )
        select
            fn.customer, fn.contact, communication_medium, min(fn.days_since_last_communication) days_since_last_communication
        from 
            fn
        where 
            fn.customer is not null
        group by 
            fn.customer, fn.contact, communication_medium
        """.format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
        # debug=True,
    )

    if not data:
        return [], []

    df = pandas.DataFrame.from_records(data)

    df1 = pandas.pivot_table(
        df,
        values="days_since_last_communication",
        index=["customer", "contact"],
        columns=["communication_medium"],
        aggfunc="count",
        margins=True,
        margins_name="Total",
    )
    df1.drop(index="Total", axis=0, inplace=True)
    df2 = pandas.pivot_table(
        df,
        values="days_since_last_communication",
        index=["customer", "contact"],
        aggfunc=min,
    )

    df3 = df1.join(df2, rsuffix="__")
    df3 = df3.reset_index().fillna(0)
    columns = [
        dict(
            label="Customer",
            fieldname="customer",
            fieldtype="Link",
            options="Customer",
            width=165,
        ),
        dict(
            label="Contact",
            fieldname="contact",
            fieldtype="Link",
            options="Contact",
            width=165,
        ),
    ]

    columns += [
        dict(
            label="Days Since Last Communication"
            if col == "days_since_last_communication"
            else col,
            fieldname=col,
            fieldtype="Int",
            width=95,
        )
        for col in df3.columns
        if not col in ["customer", "contact"]
    ]

    data = df3.to_dict("records")
    return columns, data
