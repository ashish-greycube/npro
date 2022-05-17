import frappe

# This patch updates status field in Job Applicant with new status values


def execute():
    for d in [
        ("Screening Call", "Pending for Internal Screening"),
        ("Screening Call- Rejected", "Internal Screening Rejection"),
        ("Client CV Screening", "CV Shared with Client"),
        ("Client CV Screening- Accepted", "CV Selected for Interview"),
        ("Client CV Screening- Rejected", "CV Rejected"),
        ("Client Interview", "Interview Scheduled"),
        ("Client interview-Rejected", "Rejected by Client"),
        ("Rejected by Candidate", "Rejected by Candidate"),
    ]:
        frappe.db.sql(
            "update `tabJob Applicant` set status = %s where status = %s", d, debug=True
        )
