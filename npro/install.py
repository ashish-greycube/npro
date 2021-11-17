# -*- coding: utf-8 -*-
# Copyright (c) 2020, GreyCube Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe


def after_migrate():
    #  disable Lost Opportunity of erpnext
    frappe.db.sql("update tabReport set disabled = 1 where name = 'Lost Opportunity'")

    # delete
    for report in [
        "Customer View of Opportunities",
        "Active Opportunity Ageing Analysis by Activity",
        "Opportunity Sales Stage Reminder",
    ]:
        frappe.db.sql("delete from tabReport where name = %s", (report,))
