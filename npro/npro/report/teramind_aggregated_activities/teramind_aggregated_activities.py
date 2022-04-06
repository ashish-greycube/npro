# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, today
from numpy import record
import requests
import pandas


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters):
    out = []
    settings = frappe.get_single("NPro Settings")

    headers = {"x-access-token": settings.get_password("teramind_access_token")}
    url = "{}tm-api/v1/activity/aggregated?from={}&to={}".format(
        settings.teramind_instance, filters.get("from_date"), filters.get("to_date")
    )
    response = requests.request("GET", url, headers=headers)
    # { "date": "2022-04-06", "total": 6, "idle": 0, "agent_id": 27,
    # "name": "shellexperiencehost.exe", "app": true, "classify": 0, },

    employee_dict = frappe.db.sql(
        """
        select name employee, cast(employee_number as int) agent_id, employee_name from tabEmployee
        """,
    )
    df_employee = pandas.DataFrame(
        employee_dict, columns=["employee", "agent_id", "employee_name"]
    )
    # df_employee["agent_id"] = df_employee["agent_id"].astype("int32")

    try:
        df = pandas.DataFrame(response.json())
        out = (
            df.merge(df_employee, how="left", on=["agent_id"])
            .fillna("")
            .to_dict("records")
        )
    except Exception:
        frappe.msgprint(frappe.get_traceback())

    return out


def get_columns(filters):
    return [
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Total"),
            "fieldname": "total",
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "label": _("Idle"),
            "fieldname": "idle",
            "fieldtype": "Check",
            "width": 90,
        },
        {
            "label": _("Agent Id"),
            "fieldname": "agent_id",
            "fieldtype": "Int",
            "width": 90,
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            # "fieldtype": "Link",
            # "options": "Employee",
            "width": 250,
        },
        {
            "label": _("App/Site Name"),
            "fieldname": "name",
            "fieldtype": "Data",
            "width": 250,
        },
        {
            "label": _("App"),
            "fieldtype": "Check",
            "fieldname": "app",
            "width": 90,
        },
        {
            "label": _("Classify"),
            "fieldname": "classify",
            "fieldtype": "Int",
            "width": 110,
        },
    ]


def get_conditions(filters):
    where_clause = []

    # if filters.get("from_date"):
    #     where_clause.append("op.transaction_date >= %(from_date)s")

    return " where " + " and ".join(where_clause) if where_clause else ""
