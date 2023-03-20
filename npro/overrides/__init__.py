import frappe
from frappe.utils import get_url_to_form, cint


def set_user_consent(bootinfo):
    if frappe.db.get_value(
        "NPro User Consent",
        {"name": frappe.session.user, "docstatus": 1, "i_agree": "Yes"},
    ):
        bootinfo.is_user_consent = 1
    else:
        bootinfo.is_user_consent = 0
