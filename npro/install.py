# -*- coding: utf-8 -*-
# Copyright (c) 2020, GreyCube Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe


def after_migrate():
    frappe.db.sql("update tabReport set disabled = 1 where name = 'Lost Opportunity'")
