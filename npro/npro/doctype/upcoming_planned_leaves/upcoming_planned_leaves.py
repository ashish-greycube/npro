# Copyright (c) 2023, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate
from frappe.model.document import Document


class UpcomingPlannedLeaves(Document):
    def validate(self):
        self.set_total_days()

    def set_total_days(self):
        total_days, leave_date = 0, getdate(self.from_date)
        while leave_date <= getdate(self.to_date):
            if not leave_date.strftime("%a") in ['Fri', "Sat"]:
                total_days = total_days + 1
            leave_date = frappe.utils.add_days(leave_date, 1)
        self.total_no_of_days = total_days
