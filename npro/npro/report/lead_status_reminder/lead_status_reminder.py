# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, data
import pandas
from operator import itemgetter
import collections
from frappe.utils import (
    get_url_to_report,
)


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_columns(filters):
    return [
        dict(
            label="Lead",
            fieldtype="Link",
            options="Lead",
            fieldname="docname",
            width=160,
        ),
        dict(
            label="Lead Name",
            fieldname="lead_name",
            width=140,
        ),
        dict(
            label="Company Name",
            fieldname="company_name",
            width=140,
        ),
        dict(
            label="Status",
            fieldname="status",
            width=140,
        ),
        dict(
            label="Lead Owner",
            fieldname="lead_owner",
            width=140,
        ),
        dict(
            label="Last Updated",
            fieldname="last_updated",
            width=140,
        ),
    ]


def get_data(filters):

    data = frappe.db.sql(
        """
            with fn as
            (
            select
                ld.name docname, ld.lead_name,  ld.company_name, ld.status, ld.lead_owner,
                date(COALESCE(v.creation, ld.creation)) last_updated, lssd.stale_days,
                ROW_NUMBER() over (PARTITION by ld.name order by v.creation DESC) rn
            from 
                tabLead ld
                left outer join `tabLead Stale Status Days` lssd on lssd.active_lead_status = ld.status
                left outer join tabVersion v on v.docname = ld.name 
                and v.ref_doctype = 'Lead'
                and v.data REGEXP '.*"changed":.*().*'
                and v.data  REGEXP concat(',\n(   )("',ld.status,'")\n(  ]).*')
                where ld.status in ('New', 'Working', 'Nurturing')
            )
            select * 
            from fn
            where rn = 1 
            and DATEDIFF(CURDATE(),fn.last_updated) > fn.stale_days
            order by fn.status, fn.last_updated
        """,
        as_dict=True,
        # debug=True,
    )

    return data


def send_reminder():
    reminders = collections.defaultdict(list)
    columns, data = execute(filters=None)
    for d in data:
        reminders[d.lead_owner].append(d)

    for d in reminders:
        html = frappe.render_template(
            "frappe/templates/emails/auto_email_report.html",
            {
                "title": "Lead Reminder",
                "description": "Leads inactive",
                "date_time": frappe.utils.now(),
                "columns": columns,
                "data": reminders[d],
                "report_url": get_url_to_report(
                    "Lead Status Reminder", "Script", "Report"
                ),
                "report_name": "Lead Status Reminder",
                "edit_report_settings": "",
            },
        )

        frappe.sendmail(
            recipients="vijaywm@gmail.com",
            subject="Lead Reminder",
            message=html,
        )
