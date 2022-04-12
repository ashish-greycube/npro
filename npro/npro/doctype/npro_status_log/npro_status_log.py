# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class NProStatusLog(Document):
    pass


def make_status_log(doc, docfield_name):
    old_value = (
        None
        if doc.is_new()
        else frappe.db.get_value(doc.doctype, doc.name, docfield_name)
    )
    if not old_value == doc.get(docfield_name):
        status_doc = frappe.new_doc("NPro Status Log")
        status_doc.update(
            {
                "doc_type": doc.doctype,
                "doc_name": doc.name,
                "docfield_name": docfield_name,
                "old_value": old_value,
                "new_value": doc.get(docfield_name),
            }
        )
        status_doc.save(ignore_permissions=True)
