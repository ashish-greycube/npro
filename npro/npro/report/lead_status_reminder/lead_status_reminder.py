# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, data
import pandas
from operator import itemgetter
import collections
from frappe.utils import get_url_to_report
import json
from frappe import _


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
            label="Days since Last Status Updated",
            fieldname="last_updated_days",
            fieldtype="Int",
            width=100,
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
                {where_conditions}
            )
            select docname, lead_name, company_name, status, lead_owner, last_updated,
            DATEDIFF(CURDATE(),fn.last_updated) last_updated_days
            from fn
            where rn = 1 
            and DATEDIFF(CURDATE(),fn.last_updated) > fn.stale_days
            order by fn.status, fn.last_updated
         """.format(
            where_conditions=get_conditions(filters),
        ),
        filters,
        as_dict=True,
        # debug=True,
    )

    return data


def get_conditions(filters):
    conditions = ["ld.status in ('New', 'Working','Nurturing')"]
    if filters.get("lead_owner"):
        conditions += ["ld.lead_owner = %(lead_owner)s"]

    return conditions and " where " + " and ".join(conditions) or ""


def send_reminder():
    # bench --site <site_name> execute npro.npro.report.lead_status_reminder.lead_status_reminder.send_reminder
    if not frappe.db.exists("Auto Email Report", "Lead Status Reminder"):
        from frappe.email.smtp import get_default_outgoing_email_account

        frappe.get_doc(
            dict(
                doctype="Auto Email Report",
                report="Lead Status Reminder",
                report_type="Script Report",
                user="Administrator",
                enabled=1,
                email_to=get_default_outgoing_email_account(0).email_id,
                format="HTML",
                frequency="Daily",
                filters=json.dumps(dict(lead_owner="leads@abc.com")),
            )
        ).insert()
        frappe.db.commit()

    auto_email = frappe.get_doc("Auto Email Report", "Lead Status Reminder")

    # select lead owners for Leads created in past 3 months
    for d in frappe.db.sql(
        """
        select 
            distinct lead_owner 
        from 
            tabLead
        where 
            creation > DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
            and lead_owner is not null
        """
    ):
        auto_email.filters = json.dumps(dict(lead_owner=d[0]))
        auto_email.email_to = d[0]
        try:
            auto_email.send()
        except Exception as e:
            frappe.log_error(
                e, _("Failed to send {0} Auto Email Report").format(auto_email.name)
            )
    frappe.db.commit()
