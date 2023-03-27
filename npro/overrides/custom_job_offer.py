import frappe
from frappe import _
from erpnext.hr.doctype.job_offer.job_offer import JobOffer


class CustomJobOffer(JobOffer):
    def on_change(self):
        """override to not change job applicant status to rejected"""
        pass
