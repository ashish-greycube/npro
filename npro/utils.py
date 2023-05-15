# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import today
import json


@frappe.whitelist()
def open_mapped_doc_job_offer(source_name, target_doc=None):
    def set_missing_values(source, target):
        billing_per_month_cf = frappe.db.get_value(
            "Job Opening", source.job_title, "billing_per_month_cf"
        )
        target.billing_per_month_cf = billing_per_month_cf
        for att in frappe.get_doc("NPro Settings").get(
            "default_consultant_attachment", []
        ):
            target.append(
                "npro_attachment_cf",
                {
                    "attachment_type": att.attachment_type,
                    "is_attachment_mandatory": att.is_attachment_mandatory,
                },
            )

    doc = get_mapped_doc(
        "Job Applicant",
        source_name,
        {
            "Job Applicant": {
                "doctype": "Job Offer",
                "field_map": {
                    "job_applicant": "job_applicant",
                    "applicant_name": "applicant_name",
                    "designation": "designation",
                },
            }
        },
        target_doc,
        set_missing_values,
    )
    return doc


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
                    "job_applicant": "job_applicant",
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


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_customer_contacts(doctype, txt, searchfield, start, page_len, filters):
    from frappe.contacts.doctype.contact.contact import get_contacts_linking_to

    out = [
        (d.name,) for d in get_contacts_linking_to("Customer", filters.get("customer"))
    ]

    return txt and [d for d in out if txt in d] or out


@frappe.whitelist()
def get_resumes(applicants):
    applicants = json.loads(applicants or "[]")
    if not applicants:
        return []
    resumes = frappe.db.sql(
        """
    select tf.name , tja.customer_email_cf
    from `tabJob Applicant` tja
    inner join tabFile tf on tf.file_url = tja.resume_attachment 
    and tf.attached_to_name = tja.name and tja.name in ({})
    """.format(
            ", ".join(["%s"] * len(applicants))
        ),
        tuple(applicants),
    )

    if not resumes:
        return {"resumes": [], "recipients": "", "email_template": ""}

    email_template = frappe.db.get_single_value(
        "NPro Settings", "client_cv_screening_email_template"
    )

    return {
        "resumes": [d[0] for d in resumes],
        "recipients": resumes[0][1],
        "email_template": email_template,
    }


@frappe.whitelist()
def update_job_applicant_status_client_cv_screening(applicants):
    applicants = json.loads(applicants or "[]")
    for d in applicants:
        frappe.db.set_value("Job Applicant", d, "status", "Client CV Screening")
    frappe.db.commit()


def set_client_interview_waiting_for_feedback():
    """Hourly cron for interviews in status Pending"""

    frappe.db.sql(
        """
        update `tabJob Applicant` 
        set status = 'Client Interview-waiting for feedback'
        where name in 
        (
            select job_applicant  
            from tabInterview ti 
            where status = 'Pending' and docstatus <> 2 
            and interview_type_cf = 'Client Interview'
            and ADDTIME(scheduled_on, to_time) < %s
        )""",
        frappe.utils.now(),
    )

    frappe.db.commit()
