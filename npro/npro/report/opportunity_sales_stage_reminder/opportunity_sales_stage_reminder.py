# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
import pandas
from operator import itemgetter
import json


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_columns(filters):
    return [
        dict(
            label="Opportunity",
            fieldname="docname",
            fieldtype="Link",
            options="Opportunity",
            width=160,
        ),
        dict(
            label="Customer",
            fieldname="customer",
            width=140,
        ),
        dict(
            label="Title",
            fieldname="title",
            width=140,
        ),
        dict(
            label="Contact",
            fieldname="contact_person",
            width=140,
        ),
        dict(
            label="Type",
            fieldname="opportunity_type",
            width=90,
        ),
        dict(
            label="Date",
            fieldname="transaction_date",
            width=90,
        ),
        dict(
            label="Stage",
            fieldname="sales_stage",
            width=110,
        ),
        dict(
            label="Last Updated (D)",
            fieldname="last_updated_days",
            width=140,
        ),
        # dict(
        #     label="Stale Days",
        #     fieldname="stale_no_of_days_for_reminder_cf",
        #     width=140,
        # ),
    ]


def get_conditions(filters):
    where_clause = ["op.status = 'Open'"]
    if filters.get("opportunity_owner"):
        where_clause.append("op.opportunity_owner_cf =  %(opportunity_owner)s")

    return " where " + " and ".join(where_clause) if where_clause else ""


def get_data(filters):

    data = frappe.db.sql(
        """
            with fn as
            (
                select
                    op.name docname,
                    op.opportunity_owner_cf,
                    op.title,
                    op.contact_person,
                    op.opportunity_type,
                    op.transaction_date,
                    op.sales_stage,
                    coalesce(date(ver.creation),op.transaction_date) as 'last_updated',
                    datediff(curdate(), coalesce(date(ver.creation),op.transaction_date)) as 'last_updated_days',
                    ROW_NUMBER() OVER (PARTITION BY op.name ORDER BY ver.creation DESC) rn 
                from 
                    tabOpportunity op
                    left outer join tabUser us on us.name = op.opportunity_owner_cf
                    left outer join tabVersion ver on ver.ref_doctype = 'Opportunity' 
                    and ver.docname = op.name
                    and ver.data REGEXP '.*"changed":.*().*'
                    and ver.data REGEXP '.*"sales_stage".*'
                    and ver.data  REGEXP concat(',\n(   )("',op.sales_stage,'")\n(  ]).*')
                {where_conditions}
            )
            select 
                name docname, opportunity_owner_cf owner, title, contact_person, opportunity_type, transaction_date, sales_stage,
                 last_updated, last_updated_days, stg.stale_no_of_days_for_reminder_cf
            from fn
            inner join `tabSales Stage` stg on stg.name = fn.sales_stage
            where 
                fn.rn = 1 
                and fn.last_updated_days > coalesce(nullif(stg.stale_no_of_days_for_reminder_cf,0),365)
            order by fn.last_updated_days, fn.sales_stage
        """.format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
        # debug=True,
    )

    return data


def send_reminder():
    # bench --site <site_name> execute npro.npro.report.opportunity_sales_stage_reminder.opportunity_sales_stage_reminder.send_reminder
    if not frappe.db.exists("Auto Email Report", "Opportunity Sales Stage Reminder"):
        from frappe.email.smtp import get_default_outgoing_email_account

        frappe.get_doc(
            dict(
                doctype="Auto Email Report",
                report="Opportunity Sales Stage Reminder",
                report_type="Script Report",
                user="Administrator",
                enabled=1,
                email_to=get_default_outgoing_email_account(0),
                format="HTML",
                frequency="Daily",
                filters=json.dumps(dict(opportunity_owner="sales@abc.com")),
            )
        ).insert()
        frappe.db.commit()

    reminder = frappe.get_doc("Auto Email Report", "Opportunity Sales Stage Reminder")

    # select opportunity owners for Opportunities created in past 3 months
    for d in frappe.db.sql(
        """
        select 
            distinct opportunity_owner_cf 
        from 
            tabOpportunity
        where 
            status = 'Open' 
            and creation > DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
        """
    ):
        reminder.filters = json.dumps(dict(opportunity_owner=d[0]))
        reminder.email_to = d[0]
        try:
            reminder.send()
        except Exception as e:
            frappe.log_error(
                e, _("Failed to send {0} Auto Email Report").format(reminder.name)
            )
            frappe.throw(e)
    frappe.db.commit()
