from __future__ import unicode_literals
import frappe, json
from frappe.utils import cint
from npro.npro.doctype.npro_status_log.npro_status_log import (
    make_status_log,
    make_child_status_log,
)
from npro.api import notify_update


def on_validate_job_applicant(doc, method):
    make_status_log(doc, "status")


def on_update_interview(doc, method):
    status = ""
    if doc.interview_type_cf == "Client Interview":
        status_map = {
            "Under Review": "Hold",
            "Cleared": "Accepted",
            "Rejected": "Rejected",
        }
        if cint(
            frappe.db.get_value(
                "Job Applicant", doc.job_applicant, "is_internal_hiring_cf"
            )
        ):
            status_map["Rejected"] = "Client interview-Rejected"
        status = status_map[doc.status]
    elif doc.interview_type_cf == "Technical Interview":
        if doc.status == "Cleared":
            status = "Client CV Screening"
        elif doc.status == "Rejected":
            status = "Technical interview-Rejected"
        else:
            status = "Technical interview"

    if status:
        frappe.db.set_value("Job Applicant", doc.job_applicant, "status", status)
        frappe.db.commit()
        notify_update("Job Applicant", doc.job_applicant)


def on_validate_lead(doc, method):
    make_status_log(doc, "status")


def on_update_lead(doc, method):
    # Set Contact details in Lead update as Contact is created by ErpNext before_insert
    set_contact_details(doc)


def set_contact_details(doc):
    contact = frappe.db.get_value(
        "Dynamic Link",
        {"link_doctype": "Lead", "link_name": doc.name},
        ["parent", "name"],
        as_dict=True,
    )

    if contact:
        frappe.db.set_value(
            "Dynamic Link", contact.name, "link_title", doc.company_name
        )
        frappe.db.set_value(
            "Contact",
            contact.parent,
            {
                "department_cf": doc.department_cf,
                "linkedin_profile_cf": doc.linkedin_profile_cf,
            },
        )
    frappe.db.commit()


def on_submit_job_offer(doc, method):
    if not doc.status == "Offer Released & Awaiting Response":
        frappe.throw("Job Offer status must be Offer Released & Awaiting Response")


def on_validate_job_offer(doc, method):
    if doc.status == "Rejected":
        # if not doc.db_get("status") == "Rejected":
        frappe.db.set_value(
            "Job Applicant",
            doc.job_applicant,
            "rejected_reason_cf",
            doc.offer_rejection_reason_cf,
        )
    if doc.get("billing_per_month_cf", 0):
        doc.margin_cf = (
            100
            * (
                doc.get("billing_per_month_cf", 0)
                - doc.get("consultancy_fees_offered_usd_cf", 0)
            )
            / doc.get("billing_per_month_cf", 0)
        )


def on_validate_employee(doc, method):
    from frappe.desk.form.load import get_attachments

    # copy attachments from job offer to employee
    attachments = [d.file_name for d in get_attachments(doc.doctype, doc.name)]
    for d in frappe.get_all("Job Offer", {"job_applicant": doc.job_applicant}, limit=1):
        for att in get_attachments("Job Offer", d.name):
            print(att)
            if not att.file_name in attachments:
                _file = frappe.copy_doc(frappe.get_doc("File", att.name))
                _file.attached_to_doctype = "Employee"
                _file.attached_to_name = doc.name
                _file.save(ignore_permissions=True)


def on_update_task(doc, method):
    """
    Update status of Consultant Onboarding, Post Onboarding
    so that it executes after project has been updated by erpnext
    """
    if (
        doc.status == "Completed"
        and doc.project
        and frappe.db.get_value("Project", doc.project, "status") == "Completed"
    ):
        for dt in ("Employee Onboarding", "Consultant Post Onboarding"):
            for d in frappe.db.get_all(dt, {"project": doc.project}):
                onboarding = frappe.get_doc(dt, d.name)
                if dt == "Employee Onboarding":
                    if not onboarding.boarding_status == "Completed":
                        onboarding.boarding_status = "Completed"
                        onboarding.save()
                elif dt == "Consultant Post Onboarding":
                    if not onboarding.post_boarding_status == "Completed":
                        onboarding.post_boarding_status = "Completed"
                        onboarding.save()
        frappe.db.commit()


def on_update_consultant_onboarding(doc, method):
    if doc.date_of_joining:
        frappe.db.sql(
            """
            update `tabJob Applicant` tja 
            inner join `tabJob Opening` tjo on tjo.name = tja.job_title 
            inner join `tabOpportunity` topp on topp.name = tjo.opportunity_cf 
            inner join `tabOpportunity Consulting Detail CT` tocdc on tocdc.parent = topp.name
                and tocdc.job_opening = tjo.name 
            set tocdc.stage = 'Candidate On-Boarded',
                tocdc.employee_name = tja.applicant_name
            where tja.name = %s
        """,
            (doc.job_applicant),
        )

        frappe.db.commit()


def on_cancel_consultant_onboarding(doc, method):
    if doc.job_applicant:
        frappe.db.set_value(
            "Job Applicant",
            doc.job_applicant,
            "status",
            "Rejected by Candidate",
        )
        notify_update("Job Applicant", doc.job_applicant)


def on_validate_interview(doc, method):
    make_status_log(doc, "status")
