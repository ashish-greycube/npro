from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.utils import cint, flt
from npro.npro.doctype.npro_status_log.npro_status_log import (
    make_status_log,
    set_status_and_log,
)
from npro.api import notify_update


def on_update_job_applicant(doc, method):
    make_status_log(doc, "status", trigger="on_update_job_applicant")


def on_update_interview_feedback(doc, method):
    make_status_log(doc, "result", trigger="on_update_interview_feedback")


def on_update_consultant_onboarding(doc, method):
    make_status_log(doc, "boarding_status", trigger="on_update_consultant_onboarding")


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
    make_status_log(doc, "status", trigger="on_update_interview")

    is_internal_hiring = cint(
        frappe.db.get_value("Job Applicant", doc.job_applicant, "is_internal_hiring_cf")
    )

    ja_status = None
    if doc.interview_type_cf == "Client Interview" and not is_internal_hiring:
        ja_status = {
            "Pending": "Client Interview",
            "Rejected": "Client interview-Rejected",
            "Under Review": "Hold",
            "Cleared": "Accepted",
        }.get(doc.status)
    elif doc.interview_type_cf == "Technical Interview" and not is_internal_hiring:
        ja_status = {
            "Pending": "Technical interview",
            "Rejected": "Technical interview- Rejected",
            "Under Review": "Hold",
            "Cleared": "Technical Interview- Accepted",
        }.get(doc.status)
    elif doc.interview_type_cf == "Technical Interview" and is_internal_hiring:
        ja_status = {
            "Pending": "Technical interview",
            "Rejected": "Technical interview- Rejected",
            "Under Review": "Hold",
            "Cleared": "Accepted",
        }.get(doc.status)

    if ja_status:
        set_status_and_log(
            "Job Applicant",
            doc.job_applicant,
            "status",
            ja_status,
            trigger="on_update_interview",
            commit=True,
        )
        notify_update("Job Applicant", doc.job_applicant)


def on_update_lead(doc, method):
    # Set Contact details in Lead update as Contact is created by ErpNext
    # before_insert
    set_contact_details(doc)
    make_status_log(doc, "status", trigger="on_update_lead")


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
    if doc.status not in ("Accepted", "Rejected"):
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


def on_update_after_submit_job_offer(doc, method):
    if doc.status == "Rejected":
        # change Job Applicant status to 'Rejected by Candidate' and set
        # rejection reason
        if frappe.db.get_value(
            "Job Applicant",
            {"name": doc.job_applicant, "status": ("!=", "Rejected by Candidate")},
        ):
            set_status_and_log(
                "Job Applicant",
                doc.job_applicant,
                "status",
                "Rejected by Candidate",
                trigger="on_update_after_submit_job_offer",
            )

            for r in frappe.get_all(
                "Npro Rejected Reason Detail",
                filters={"parent": doc.name},
                fields=["name", "rejected_reason"],
            ):
                frappe.get_doc(
                    {
                        "doctype": "Npro Rejected Reason Detail",
                        "parent": doc.job_applicant,
                        "parentfield": "rejected_reason_cf",
                        "parenttype": "Job Applicant",
                        "rejected_reason": r.rejected_reason,
                    }
                ).insert()
            frappe.db.commit()


def on_update_job_offer(doc, method):
    # if doc.db_get("status") == "Sent for Approval":
    #     if doc.offer_approver_cf == frappe.session.user:
    #         doc.offer_approved_by_cf = frappe.session.user
    #     else:
    #         frappe.throw(_("Not allowed to change Job Offer"))
    # if doc.status == "Offer Approved":
    #     if not doc.offer_approver_cf:
    #         doc.offer_approver_cf = frappe.session.user
    make_status_log(doc, "status", "on_update_job_offer")


def on_validate_employee(doc, method):
    from frappe.desk.form.load import get_attachments

    # copy attachments from job offer to employee
    attachments = [d.file_name for d in get_attachments(doc.doctype, doc.name)]
    for d in frappe.get_all("Job Offer", {"job_applicant": doc.job_applicant}, limit=1):
        for att in get_attachments("Job Offer", d.name):
            print(att)
            if att.file_name not in attachments:
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


def after_insert_consultant_onboarding(doc, method):
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


@frappe.whitelist()
def cancel_consultant_onboarding(name, rejection_reasons=""):
    """Cannot cancel Employee On Boarding without cancelling linked docs.
    So setting status to Cancelled and changing docstatus to 2"""
    frappe.set_value("Employee Onboarding", name, "boarding_status", "Cancelled")
    frappe.db.set_value("Employee Onboarding", name, "docstatus", 2)

    status_doc = frappe.new_doc("NPro Status Log")
    status_doc.update(
        {
            "doc_type": "Employee Onboarding",
            "doc_name": name,
            "docfield_name": "boarding_status",
            "old_value": frappe.db.get_value(
                "Employee Onboarding", name, "boarding_status"
            ),
            "new_value": "Cancelled",
        }
    )
    status_doc.save(ignore_permissions=True)

    rejection_reasons = json.loads(rejection_reasons or "[]")

    doc = frappe.get_doc("Employee Onboarding", name)
    existing_reasons = frappe.get_all(
        "Npro Rejected Reason Detail",
        filters={"parent": name},
        fields=["rejected_reason"],
        pluck="rejected_reason",
    )

    for d in rejection_reasons:
        if d["rejected_reason"] in existing_reasons:
            continue
        reason = doc.append(
            "rejection_reason_cf", {"rejected_reason": d["rejected_reason"]}
        )
        reason.save()

    # set consultant name null in Opportunity Consultant detail
    for d in frappe.db.sql(
        """
        select name , parent
        from `tabOpportunity Consulting Detail CT`
        where job_opening = %s and employee_name = %s
    """,
        (applicant.job_title, applicant.applicant_name),
    ):
        frappe.db.set_value(
            "Opportunity Consulting Detail CT", d[0], "employee_name", None
        )
        frappe.get_doc("Opportunity", d[1]).reload()

    # Job Applicant
    applicant = frappe.get_doc("Job Applicant", doc.job_applicant)
    existing_reasons = frappe.get_all(
        "Npro Rejected Reason Detail",
        filters={"parent": doc.job_applicant},
        fields=["rejected_reason"],
        pluck="rejected_reason",
    )

    for d in rejection_reasons:
        if d["rejected_reason"] in existing_reasons:
            continue
        reason = applicant.append(
            "rejected_reason_cf", {"rejected_reason": d["rejected_reason"]}
        )
        reason.save()

    applicant.status = "Rejected by Candidate"
    applicant.save()
    notify_update("Job Applicant", doc.job_applicant)

    # Job Offer Cancelled
    if frappe.db.get_value(
        "Job Offer", {"name": doc.job_offer, "status": ("!=", "Rejected")}
    ):
        frappe.db.set_value("Job Offer", doc.job_offer, "status", "Rejected")
        offer = frappe.get_doc("Job Offer", doc.job_offer)
        existing_reasons = frappe.get_all(
            "Npro Rejected Reason Detail",
            filters={"parent": doc.job_offer},
            fields=["rejected_reason"],
            pluck="rejected_reason",
        )

        for d in rejection_reasons:
            if d["rejected_reason"] in existing_reasons:
                continue
            reason = offer.append(
                "offer_rejection_reason_cf", {"rejected_reason": d["rejected_reason"]}
            )
            reason.save()
        frappe.get_doc("Job Offer", doc.job_offer).cancel()

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
            frappe.get_doc("Project", doc.project).db_set(
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
                set_status_and_log(
                    "Job Applicant",
                    job_applicant,
                    "status",
                    "Client Interview",
                    trigger="after_insert_communication",
                    commit=True,
                )
                notify_update("Job Applicant", job_applicant)
    except Exception:
        frappe.log_error(frappe.get_traceback())


@frappe.whitelist()
def get_boarding_status(project):
    status = "Pending"
    if project:
        doc = frappe.get_doc("Project", project)
        if doc.status == "Cancelled":
            return "Cancelled"
        if flt(doc.percent_complete) > 0.0 and flt(doc.percent_complete) < 100.0:
            status = "In Process"
        elif flt(doc.percent_complete) == 100.0:
            status = "Completed"
        return status
