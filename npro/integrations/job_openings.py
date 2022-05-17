from __future__ import unicode_literals
import frappe, json
from werkzeug.wrappers import Response
from frappe.utils.response import as_json


@frappe.whitelist(allow_guest=False)
def job_opening(**args):
    """List of current Job Openings in Open status."""
    args["search_term"] = "%%{}%%".format(args.get("s"))

    conditions = []
    if args.get("name"):
        conditions += [" tjo.name = %(name)s"]
    if args.get("s"):
        conditions += [
            " (tjo.job_title like %(search_term)s or tjo.description like %(search_term)s) "
        ]
    if args.get("location"):
        conditions += [" tjo.location_cf = %(location)s"]
    if args.get("module"):
        conditions += [" tbm.website_service = %(module)s"]

    conditions = conditions and " and " + " and ".join(conditions) or ""

    data = frappe.db.sql(
        """
    select 
        tjo.name, tjo.location_cf , tjo.job_title , tjo.description , tbm.website_service
    from 
        `tabJob Opening` tjo
        left outer join tabOpportunity topp on topp.name  = tjo.opportunity_cf 
        left outer join `tabBusiness Module Website Service Mapping` tbm on tbm.opportunity_business_module = topp.business_module 
    where 
        tjo.status = 'Open' {conditions}
    """.format(
            conditions=conditions
        ),
        args,
        as_dict=True,
    )

    response = as_json()
    response.data = frappe.as_json(data)
    return response
