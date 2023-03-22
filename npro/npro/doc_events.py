from __future__ import unicode_literals
import frappe, json
from frappe import _
from frappe.utils import cint, flt
from npro.npro.doctype.npro_status_log.npro_status_log import (
    make_status_log,
    make_child_status_log,
)
from npro.api import notify_update


def on_validate_job_applicant(doc, method):
    make_status_log(doc, "status")


def on_validate_interview_feedback(doc, method):
    make_status_log(doc, "result")


def on_validate_consultant_onboarding(doc, method):
    make_status_log(doc, "status")


def on_submit_interview_feedback(doc, method):
    if not doc.result:
        frappe.throw(_("Interview Feedback status has to be Cleared or Rejected"))
    interview = frappe.get_doc("Interview", doc.interview)
    interview.status = doc.result
    interview.save()
    # update Job Opening
    if doc.result == "Cleared" and interview.interview_type_cf == "Technical Interview":
        frappe.set_value(
            "Job Opening", interview.job_opening, "inform_all_stakeholder_cf", 1
        )


def on_update_interview(doc, method):
    status = ""
    if doc.interview_type_cf == "Client Interview":
        is_internal_hiring = cint(
            frappe.db.get_value(
                "Job Applicant", doc.job_applicant, "is_internal_hiring_cf"
            )
        )
        status = {
            "Under Review": "Hold",
            "Cleared": "Accepted",
            "Rejected": "Rejected"
            if is_internal_hiring
            else "Client interview-Rejected",
        }.get(doc.status)

    elif doc.interview_type_cf == "Technical Interview":
        status = {
            "Cleared": "Client CV Screening",
            "Rejected": "Technical interview-Rejected",
        }.get(doc.status) or "Technical interview"

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
    if not doc.status in ("Accepted", "Rejected"):
        frappe.throw(
            _("Job Offer cannot be submitted in status {0}").format(doc.status)
        )

        # validate attachments
        missing = []
        for att in frappe.get_doc("NPro Settings").get(
            "default_consultant_attachment", []
        ):
            if cint(att.is_attachment_mandatory):
                if not len(
                    [
                        d
                        for d in doc.npro_attachment_cf
                        if d.attachment_type == att.attachment_type
                    ]
                ):
                    missing.append(att.attachment_type)
        if missing:
            frappe.throw(_("Attachments missing: {0}").format(",".join(missing)))


def on_update_job_offer(doc, method):
    if doc.status == "Rejected":
        # frappe.flags.rejected_reasons = [
        #     d.rejected_reason for d in doc.offer_rejection_reason_cf
        # ]

        # Cancel Consultant Onboarding, by setting status = Cancelled
        onboarding = frappe.db.get_value(
            "Employee Onboarding", {"job_offer": doc.name, "docstatus": 1}
        )
        if onboarding:
            frappe.get_doc("Employee Onboarding", onboarding).db_set(
                "status",
                "Cancelled",
                update_modified=True,
                notify=True,
            )


def on_validate_job_offer(doc, method):
    if doc.status == "Offer Approved":
        if not doc.offer_approver_cf:
            doc.offer_approver_cf = frappe.session.user
    make_status_log(doc, "status")


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

    if doc.status in ("Cancelled",):
        # Job Offer Cancelled
        jo = frappe.db.get_value(
            "Job Offer", {"name": doc.job_offer, "status": ("!=", "Cancelled")}
        )
        if jo:
            frappe.get_doc("Job Offer", jo).cancel()

        # set applicant Rejected by Candidate
        # frappe.flags.rejected_reasons = [
        #     d.rejected_reason for d in doc.offer_rejection_reason_cf
        # ]

        # Open Tasks and Internal Project: status Cancelled
        if doc.project:
            if frappe.db.exists(
                "Project",
                {
                    "name": doc.project,
                    "project_type": "Internal",
                    "status": ("!=", "Cancelled"),
                },
            ):
                frappe.get_doc("Project", doc.project).db._set(
                    "status",
                    "Cancelled",
                    update_modified=True,
                    notify=True,
                )
            for task in frappe.db.get_list(
                "Task",
                {
                    "project": doc.project,
                    "status": ("not in", ["Cancelled", "Completed"]),
                },
            ):
                frappe.get_doc("Task", task).db_set(
                    "status",
                    "Cancelled",
                    update_modified=True,
                    notify=True,
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


def after_insert_communication(doc, method):
    try:
        if (
            doc.communication_type == "Communication"
            and doc.get("reference_doctype") == "Interview"
            and doc.sent_or_received == "Sent"
        ):
            job_applicant, interview_type_cf = frappe.db.get_value(
                "Interview", doc.reference_name, ["job_applicant", "interview_type_cf"]
            )
            if interview_type_cf == "Client Interview":
                frappe.db.set_value(
                    "Job Applicant", job_applicant, "status", "Client Interview"
                )
                notify_update("Job Applicant", job_applicant)
    except Exception:
        frappe.log_error(frappe.get_traceback())
