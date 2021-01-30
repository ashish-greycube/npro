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
            label="Contact",
            fieldname="contact",
            fieldtype="Link",
            options="Contact",
            width=165,
        ),
        dict(
            label="Customer",
            fieldname="customer",
            fieldtype="Link",
            options="Customer",
            width=165,
        ),
        dict(label="Phone", fieldname="mobile_no", width=110),
        dict(label="Email Id", fieldname="email_id", width=110),
        dict(label="Linkedin Profile Id", fieldname="linkedin_profile_cf", width=130),
        dict(
            label="Last Communicated On",
            fieldname="communication_date",
            fieldtype="Date",
            width=170,
        ),
        dict(
            label="Last Communication Medium",
            fieldname="communication_medium",
            width=170,
        ),
        dict(
            label="Communication Frequency",
            fieldname="communication_frequency_in_days_cf",
            fieldtype="Int",
            width=160,
        ),
    ]


def get_conditions(filters):
    where_clause = []
    if filters.get("account_manager"):
        where_clause.append("cus.account_manager =  %(account_manager)s")

    return " and " + " and ".join(where_clause) if where_clause else ""


def get_data(filters):

    data = frappe.db.sql(
        """
            with fn as 
            (
                select 
                    date(comm.communication_date) communication_date, cml.link_name contact, comm.communication_medium, 
                    ROW_NUMBER() OVER (PARTITION BY cml.link_name ORDER BY comm.communication_date DESC) rn
                    from tabCommunication comm 
                    inner join `tabCommunication Link` cml on cml.parent = comm.name
                    and cml.link_doctype = 'Contact'
                    left outer join tabEvent et on et.name = comm.reference_name
                    and comm.reference_doctype = 'Event' and et.status = 'Open'
                where comm.reference_doctype <> 'Event' or et.name is NULL
            )
            select 
                cus.name customer, dl.parent contact, ct.phone, ct.mobile_no, ct.email_id, 
                ct.communication_frequency_in_days_cf, fn.communication_date, ct.linkedin_profile_cf,
                fn.communication_medium, ifnull(DATEDIFF(CURDATE(), fn.communication_date),365)
            from tabCustomer cus
                left outer join `tabDynamic Link` dl on dl.link_doctype = 'Customer' 
                and dl.parenttype = 'Contact' and dl.link_name = cus.name
                left outer join tabContact ct on ct.name = dl.parent
                left outer join fn on fn.contact = ct.name and fn.rn = 1 
            where 
                communication_frequency_in_days_cf <> 0
                and communication_frequency_in_days_cf <  ifnull(DATEDIFF(CURDATE(), fn.communication_date),365) 
                {where_conditions}
        """.format(
            where_conditions=get_conditions(filters)
        ),
        filters,
        as_dict=True,
        # debug=True,
    )

    return data


def send_reminder():
    # bench --site <site_name> execute npro.npro.report.customer_contactwise_communication_frequency_alert.customer_contactwise_communication_frequency_alert.send_reminder
    if not frappe.db.exists(
        "Auto Email Report", "Customer Contactwise Communication Frequency Alert"
    ):
        from frappe.email.smtp import get_default_outgoing_email_account

        frappe.get_doc(
            dict(
                doctype="Auto Email Report",
                report="Customer Contactwise Communication Frequency Alert",
                report_type="Script Report",
                user="Administrator",
                enabled=1,
                email_to=get_default_outgoing_email_account(0).login_id,
                format="HTML",
                frequency="Daily",
                filters=json.dumps(dict(account_manager="accounts@abc.com")),
            )
        ).insert()
        frappe.db.commit()

    auto_email = frappe.get_doc(
        "Auto Email Report", "Customer Contactwise Communication Frequency Alert"
    )

    # select account_managers
    for d in frappe.db.sql(
        """
        select 
            distinct account_manager 
        from 
            tabCustomer
        where account_manager is not null
        """
    ):
        auto_email.filters = json.dumps(dict(account_manager=d[0]))
        auto_email.email_to = d[0]
        try:
            auto_email.send()
        except Exception as e:
            frappe.log_error(
                e, _("Failed to send {0} Auto Email Report").format(auto_email.name)
            )
    frappe.db.commit()