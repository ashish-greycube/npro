from __future__ import unicode_literals
import frappe, json
from werkzeug.wrappers import Response
from frappe.utils.response import as_json



@frappe.whitelist(allow_guest=True)
def job_opening():
    """List of current Job Openings in Open status."""

    data = frappe.db.sql(
        """
    select 
        tjo.name, tjo.location_cf , tjo.job_title , tjo.description , tbm.website_service
    from 
        `tabJob Opening` tjo
        left outer join tabOpportunity topp on topp.name  = tjo.opportunity_cf 
        left outer join `tabBusiness Module Website Service Mapping` tbm on tbm.opportunity_business_module = topp.business_module 
    where 
        tjo.status = 'Open'
    """,
        as_dict=True,
    )

    response = as_json()
    response.data = frappe.as_json(data)
    return response


@frappe.whitelist()
def job_opening_test():
    """List of current Job Openings in Open status."""
    return ""
    data = frappe.db.sql(
        """
    select 
        tjo.name, tjo.location_cf , tjo.job_title , tjo.description , tbm.website_service
    from 
        `tabJob Opening` tjo
        left outer join tabOpportunity topp on topp.name  = tjo.opportunity_cf 
        left outer join `tabBusiness Module Website Service Mapping` tbm on tbm.opportunity_business_module = topp.business_module 
    where 
        tjo.status = 'Open'
    """,
        as_dict=True,
    )

    response = as_json()
    response.data = frappe.as_json(data)
    return response

