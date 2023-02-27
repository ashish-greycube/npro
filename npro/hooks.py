# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "npro"
app_title = "NPro"
app_publisher = "GreyCube Technologies"
app_description = "Customization for NPro Pte Ltd"
app_icon = "octicon octicon-people"
app_color = "orange"
app_email = "admin@greycube.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/npro/css/npro.css"
app_include_js = "/assets/npro/js/npro.js"

# include js, css files in header of web template
# web_include_css = "/assets/npro/css/npro.css"
# web_include_js = "/assets/npro/js/npro.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "npro/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Lead": "public/js/lead.js",
    "Opportunity": "public/js/opportunity.js",
    "Contact": "public/js/contact.js",
    "Job Opening": "public/js/job_opening.js",
    "Job Offer": "public/js/job_offer.js",
    "Job Applicant": "public/js/job_applicant.js",
    "Interview": "public/js/interview.js",
    "Employee": "public/js/employee.js",
    "Project": "public/js/project.js",
}
doctype_list_js = {"Job Applicant": "public/js/job_applicant_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

before_install = "npro.api.remove_standard_crm_values"
# after_install = "npro.install.after_install"
after_migrate = "npro.install.after_migrate"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "npro.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    # 	"ToDo": "custom_app.overrides.CustomToDo"
    "Interview": "npro.overrides.custom_interview.CustomInterview"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Opportunity": {
        "on_update": [
            "npro.api.on_update_opportunity",
            "npro.npro.controllers.opportunity.on_update_opportunity",
        ],
        "validate": [
            "npro.api.on_validate_opportunity",
            "npro.npro.controllers.opportunity.on_validate_opportunity",
        ],
    },
    "Interview": {
        "on_update": [
            "npro.api.on_update_interview",
            "npro.npro.doc_events.on_update_interview",
        ]
    },
    "Job Offer": {
        "on_submit": "npro.npro.doc_events.on_submit_job_offer",
        "validate": "npro.npro.doc_events.on_validate_job_offer",
    },
    "Job Opening": {
        "autoname": "npro.api.autoname_job_opening",
        "on_update": "npro.api.on_update_job_opening",
        "validate": [
            "npro.api.validate_job_opening",
        ],
    },
    "Lead": {
        "validate": "npro.npro.doc_events.on_validate_lead",
        "on_update": "npro.npro.doc_events.on_update_lead",
    },
    "Job Applicant": {
        "on_update": "npro.api.on_update_job_applicant",
        "validate": "npro.npro.doc_events.on_validate_job_applicant",
    },
    "Employee": {
        "validate": "npro.npro.doc_events.on_validate_employee",
    },
    "Task": {
        "on_update": "npro.npro.doc_events.on_update_task",
    },
    "Employee Onboarding": {
        "on_update_after_submit": "npro.npro.doc_events.on_update_consultant_onboarding",
        "on_update": "npro.npro.doc_events.on_update_consultant_onboarding",
    },
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": [
        "npro.npro.report.lead_status_reminder.lead_status_reminder.send_reminder",
        "npro.npro.report.opportunity_sales_stage_reminder.opportunity_sales_stage_reminder.send_reminder",
        "npro.npro.report.customer_contactwise_communication_frequency_alert.customer_contactwise_communication_frequency_alert.send_reminder",
    ]
    # 	"all": [
    # 		"npro.tasks.all"
    # 	],
    # 	"hourly": [
    # 		"npro.tasks.hourly"
    # 	],
    # 	"weekly": [
    # 		"npro.tasks.weekly"
    # 	]
    # 	"monthly": [
    # 		"npro.tasks.monthly"
    # 	]
}

# Testing
# -------

# before_tests = "npro.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "npro.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "npro.task.get_dashboard_data"
# }
fixtures = [
    {
        "dt": "Property Setter",
        "filters": [["name", "in", ["Opportunity-Allow events in timeline"]]],
    },
    {
        "dt": "Lead Source",
        "filters": [
            [
                "name",
                "in",
                [
                    "Tele calling referral",
                    "Tele calling",
                    "LinkedIn",
                    "Campaign",
                    "Mass Mailing",
                    "Cold Calling",
                    "Advertisement",
                    "Reference",
                    "Existing Customer",
                ],
            ]
        ],
    },
    {"dt": "Opportunity Type", "filters": [["name", "in", ["Project", "Consulting"]]]},
    {
        "dt": "Sales Stage",
        "filters": [
            [
                "name",
                "in",
                [
                    "Completed",
                    "Discovery Call",
                    "NPro Candidate Sourcing",
                    "Client Interview",
                    "Client CV Screening",
                    "Candidate Approved",
                    "New",
                    "Negotiation",
                    "Proposal Sent",
                    "Needs Analysis",
                ],
            ]
        ],
    },
]
# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]
