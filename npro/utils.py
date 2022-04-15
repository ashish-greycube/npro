# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def make_consultant_from_job_offer(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.customer_cf = source.customer_cf
        target.scheduled_confirmation_date = source.offer_date
        target.joining_consultancy_fees_inr_cf = source.consultancy_fees_offered_cf
        target.joining_consultancy_fees_usd_cf = source.consultancy_fees_offered_usd_cf

        # fields from Job Applicant
        for d in frappe.db.get_all(
            "Job Applicant",
            fields=[
                "email_id",
                "applicant_name",
                "current_salary_cf",
                "current_salary_usd_cf",
            ],
            filters={"name": source.job_applicant},
            limit=1,
        ):
            target.personal_email = d.email_id
            target.first_name = d.applicant_name
            target.previous_salary_inr_cf = d.current_salary_cf
            target.previous_salary_usd_cf = d.current_salary_usd_cf

    doc = get_mapped_doc(
        "Job Offer",
        source_name,
        {
            "Job Offer": {
                "doctype": "Employee",
                "field_map": {
                    "applicant_name": "employee_name",
                    "designation": "designation",
                    "company": "company",
                    "expected_doj_cf": "date_of_joining",
                },
            }
        },
        target_doc,
        set_missing_values,
    )

    return doc
