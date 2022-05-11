from __future__ import unicode_literals
import frappe, json


def on_validate_job_applicant(doc, method):
    from npro.npro.doctype.npro_status_log.npro_status_log import make_status_log

    make_status_log(doc, "status")


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
