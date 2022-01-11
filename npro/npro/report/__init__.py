# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
import shutil, os
from frappe.modules import scrub, get_module_path


def copy_report(
    module="NPro",
    src="Job Applicant Details",
    tgt="Rejected Candidates",
):
    """usage: copy_report("NPro", "src", "tgt")"""

    doc = frappe.copy_doc(frappe.get_doc("Report", src))
    doc.report_name = tgt
    doc.insert()
    frappe.db.commit()

    print('Copying "' + src + '" to "' + tgt, '"')
    module_path = get_module_path(module)
    src_folder = module_path and os.path.join(module_path, "report", scrub(src))
    src_path = os.path.join(src_folder, scrub(src) + ".py")
    src_script_path = src_folder and os.path.join(src_folder, scrub(src) + ".js")

    tgt_folder = module_path and os.path.join(module_path, "report", scrub(tgt))
    tgt_path = os.path.join(tgt_folder, scrub(tgt) + ".py")
    tgt_script_path = tgt_folder and os.path.join(tgt_folder, scrub(tgt) + ".js")

    shutil.copyfile(src_path, tgt_path)
    shutil.copyfile(src_script_path, tgt_script_path)

    print(src_path, tgt_path)
    print(src_script_path, tgt_script_path)
