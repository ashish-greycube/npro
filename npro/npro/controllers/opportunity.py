from __future__ import unicode_literals
import frappe
import json
from frappe.utils import cint
from npro.npro.doctype.npro_status_log.npro_status_log import (
    make_child_status_log,
)


def on_update_opportunity(doc, method):
    for d in doc.opportunity_consulting_detail_ct_cf:
        job_opening = d.get("job_opening")
        if job_opening:
            jo = frappe.get_doc("Job Opening", job_opening)
            # doc.job_title = ?
            jo.location_cf = d.location
            jo.contract_duration_cf = cint(d.duration_in_months)
            jo.billing_per_month_cf = d.billing_per_month

            if doc.contact_person:
                jo.customer_contact_cf = doc.contact_person
            if d.project_name:
                jo.opportunity_technology_cf = d.project_name

            # set JO status to Closed if Opp requirement is Lost
            if d.stage == "Lost" and not jo.status == "Lost":
                jo.status = "Lost"
                jo.lost_reason_cf = (
                    "The opportunity was lost hence the Job Opening is set to lost."
                )
            jo.save(
                ignore_permissions=True,
            )
    frappe.db.commit()


def on_validate_opportunity(doc, method):
    make_child_status_log(doc, "opportunity_consulting_detail_ct_cf", "stage")
