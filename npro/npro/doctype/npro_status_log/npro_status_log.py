# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class NProStatusLog(Document):
    pass


def make_child_status_log(doc, docfield_name, child_docfield_name):
    children = doc.get(docfield_name)
    children_before_save = []
    if doc.get_doc_before_save():
        children_before_save = doc.get_doc_before_save().get(docfield_name)

    for d in children:
        old_value = None
        original = [i for i in children_before_save if i.name == d.name]
        if original:
            old_value = original[0].get(child_docfield_name)
            if old_value == d.get(child_docfield_name):
                continue

        frappe.get_doc(
            {
                "doctype": "NPro Status Log",
                "doc_type": doc.doctype,
                "doc_name": doc.name,
                "docfield_name": docfield_name,
                "child_doc_type": d.doctype,
                "child_doc_name": d.name,
                "child_docfield_name": child_docfield_name,
                "old_value": old_value,
                "new_value": d.get(child_docfield_name),
            }
        ).save(ignore_permissions=True)


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
    frappe.db.commit()


def get_last_status(doc_type, doc_name, docfield_name="status"):
    return frappe.db.get_value(
        "NPro Status Log",
        filters={
            "doc_type": doc_type,
            "doc_name": doc_name,
            "docfield_name": docfield_name,
        },
        order_by="creation desc",
        fieldname=["old_value", "new_value"],
        as_dict=True,
    )


def set_status_and_log(doctype, docname, docfield_name, new_value, commit=True):
    old_value = None
    if frappe.db.exists(doctype, docname):
        old_value = frappe.db.get_value(doctype, docname, docfield_name)
    last_log = get_last_status(doctype, docname, docfield_name)
    if not last_log or not last_log.new_value == new_value:
        frappe.get_doc(
            {
                "doctype": "NPro Status Log",
                "doc_type": doctype,
                "doc_name": docname,
                "docfield_name": docfield_name,
                "old_value": old_value,
                "new_value": new_value,
            }
        ).save(ignore_permissions=True)
        if commit:
            frappe.db.commit()
