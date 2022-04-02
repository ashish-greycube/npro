# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.hr.utils import EmployeeBoardingController


class ConsultantPostOnboarding(EmployeeBoardingController):
    def validate(self):
        super(ConsultantPostOnboarding, self).validate()

    def on_submit(self):
        # create the project for the given employee onboarding
        project_name = _(self.doctype) + " : " + self.employee

        project = frappe.get_doc(
            {
                "doctype": "Project",
                "project_name": project_name,
                "expected_start_date": frappe.utils.today(),
                "department": self.department,
                "company": self.company,
            }
        ).insert(ignore_permissions=True, ignore_mandatory=True)

        self.db_set("project", project.name)
        self.db_set("post_boarding_status", "Pending")
        self.reload()
        self.create_task_and_notify_user()

    def on_update_after_submit(self):
        self.create_task_and_notify_user()

    def on_cancel(self):
        super(ConsultantPostOnboarding, self).on_cancel()
