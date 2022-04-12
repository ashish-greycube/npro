from __future__ import unicode_literals
import frappe, json


def on_validate_job_applicant(doc, method):
    from npro.npro.doctype.npro_status_log.npro_status_log import make_status_log

    make_status_log(doc, "status")
