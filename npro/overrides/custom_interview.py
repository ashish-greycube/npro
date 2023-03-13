import frappe
from frappe import _
from erpnext.hr.doctype.interview.interview import Interview
from erpnext.hr.doctype.interview.interview import get_recipients


class CustomInterview(Interview):
    """
    Custom class to override erpnext.
    Fixes bug in reschedule_interview, where both old and new scheduled dates are same.
    Updates Job Applicant status to
    """

    @frappe.whitelist()
    def reschedule_interview(self, scheduled_on, from_time, to_time):
        original_date = self.scheduled_on
        original_from_time = self.from_time
        original_to_time = self.to_time

        self.db_set(
            {"scheduled_on": scheduled_on, "from_time": from_time, "to_time": to_time}
        )
        self.notify_update()
        frappe.db.set_value(
            "Job Applicant",
            self.job_applicant,
            "status",
            "Client Interview-rescheduled",
        )

        recipients = get_recipients(self.name)

        message = _(
            "Your Interview session is rescheduled from {0} {1} - {2} to {3} {4} - {5}"
        ).format(
            original_date,
            original_from_time,
            original_to_time,
            scheduled_on,
            from_time,
            to_time,
        )

        try:
            frappe.sendmail(
                recipients=recipients,
                subject=_("Interview: {0} Rescheduled").format(self.name),
                message=_(
                    "Your Interview session is rescheduled from {0} {1} - {2} to {3} {4} - {5}"
                ).format(
                    original_date,
                    original_from_time,
                    original_to_time,
                    self.scheduled_on,
                    from_time,
                    to_time,
                ),
                reference_doctype=self.doctype,
                reference_name=self.name,
            )
            frappe.msgprint(_("Interview rescheduled successfully"), indicator="green")
        except Exception:
            frappe.msgprint(
                _(
                    "Failed to send the Interview Reschedule notification. Please configure your email account."
                )
            )
