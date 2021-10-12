# Copyright (c) 2013, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_columns(filters):
    return [
        dict(
            label="Customer",
            fieldname="name",
            fieldtype="Link",
            options="Customer",
            width=200,
        ),
        dict(
            label="Customer Name",
            fieldname="customer_name",
            width=200,
        ),
        dict(label="Contacts Count", fieldname="ct", fieldtype="Int", width=90),
        dict(
            label="Customer Group",
            fieldname="customer_group",
            width=200,
        ),
        dict(
            label="Account Manager",
            fieldname="account_manager",
            width=150,
        ),
        dict(
            label="Industry",
            fieldname="industry",
            width=150,
        ),
        dict(
            label="Application",
            fieldname="application",
            width=200,
        ),
        dict(
            label="Vendor",
            fieldname="vendor",
            width=200,
        ),
    ]


def get_data(filters):
    return frappe.db.sql(
        """
	select 
		name, customer_name, con.ct, c.customer_group, c.account_manager, c.industry,
		app.application, vend.vendor
	from tabCustomer c
	left outer join 
		(
			select dl.link_name, count(*) ct from `tabDynamic Link` dl where dl.link_doctype = 'Customer' 
			and dl.parenttype = 'Contact' group by link_name
		) con on con.link_name = c.name
	left outer join 
		(
			select parent, group_concat(application) application
			from `tabApplications CT` group by parent
		) app on app.parent = c.name
	left outer join 
		(
			select parent, group_concat(vendor) vendor
			from `tabVendor Project Service CT` group by parent
		) vend on vend.parent = c.name

	"""
    )
