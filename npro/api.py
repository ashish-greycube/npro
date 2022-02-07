from __future__ import unicode_literals
import frappe, json
from frappe.utils import (
    getdate,
    add_days,
    today,
    flt,
    get_datetime,
    formatdate,
    get_datetime_in_timezone,
    get_time_zone,
    format_datetime,
)
import pytz
from frappe.model.naming import make_autoname

from frappe.desk.form.load import get_attachments
from frappe.email.doctype.notification.notification import evaluate_alert


def on_update_opportunity(doc, method):
    set_status_value(doc, method)

    # send email for job creation

    notification = (
        frappe.db.get_single_value("NPro Settings", "candidate_sourcing_notification")
        or ""
    )

    if notification:
        job_openings = [
            d
            for d in doc.opportunity_consulting_detail_ct_cf
            if d.stage == "NPro Candidate Sourcing"
            and not d.email_sent_for_job_opening_creation
        ]

        if job_openings:
            for detail in job_openings:
                doc.consulting_detail = detail
                evaluate_alert(doc, notification, "Custom")
            for d in job_openings:
                frappe.db.set_value(
                    "Opportunity Consulting Detail CT",
                    d.name,
                    "email_sent_for_job_opening_creation",
                    1,
                )
            frappe.db.commit()


def on_validate_opportunity(doc, method):
    opportunity_cost_calculation(doc, method)
    notify_sales_stage_update(doc, method)


@frappe.whitelist()
def opportunity_cost_calculation(self, method):
    # check if expected_date in child table has passed then  stage should be  either Won or Lost
    if self.opportunity_type == "Consulting":
        for row in self.opportunity_consulting_detail_ct_cf:
            if getdate(row.expected_close_date) < getdate(
                today()
            ) and row.stage not in ["Won", "Lost", "Candidate On-Boarded"]:
                frappe.throw(
                    title="Incorrect stage in Opportunity Consulting Detail",
                    msg="Row #{0}, stage is {1}. It should be either Won or Lost or Candidate On-Boarded. Please correct it.".format(
                        frappe.bold(row.idx), row.stage
                    ),
                )
    elif self.opportunity_type == "Project":
        for row in self.opportunity_project_detail_ct_cf:
            if getdate(row.expected_close_date) < getdate(
                today()
            ) and row.stage not in ["Won", "Lost"]:
                frappe.throw(
                    title="Incorrect stage in Opportunity Project Detail",
                    msg="Row #{0}, stage is {1}. It should be either Won or Lost. Please correct it.".format(
                        frappe.bold(row.idx), row.stage
                    ),
                )

    # calculate per row amount for  Consulting
    if self.opportunity_type == "Consulting":
        for row in self.opportunity_consulting_detail_ct_cf:
            if row.duration_in_months and row.billing_per_month:
                row.amount = flt(row.duration_in_months * row.billing_per_month)

    # calculate child table grand total amount, won and lost amount
    child_table_grand_total = 0.0
    child_table_won_amount = 0.0
    child_table_lost_amount = 0.0
    if self.opportunity_type == "Consulting":
        for row in self.opportunity_consulting_detail_ct_cf:
            if row.stage in ["Won", "Candidate On-Boarded"]:
                child_table_won_amount += flt(row.amount)
            elif row.stage == "Lost":
                child_table_lost_amount += flt(row.amount)
            child_table_grand_total += flt(row.amount)
    elif self.opportunity_type == "Project":
        for row in self.opportunity_project_detail_ct_cf:
            if row.stage == "Won":
                child_table_won_amount += flt(row.amount)
            elif row.stage == "Lost":
                child_table_lost_amount += flt(row.amount)
            child_table_grand_total += flt(row.amount)

    self.won_amount_cf = child_table_won_amount
    self.lost_amount_cf = child_table_lost_amount
    self.opportunity_amount = flt(
        child_table_grand_total - child_table_won_amount - child_table_lost_amount
    )


@frappe.whitelist()
def set_status_value(self, method):
    if self.status in ["Closed", "Converted", "Lost"]:
        self.sales_stage = "Completed"


@frappe.whitelist()
def remove_standard_crm_values():
    frappe.db.delete(
        "Lead Source",
        {
            "name": [
                "not in",
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
        },
    )
    frappe.db.delete(
        "Opportunity Type", {"name": ["not in", ["Project", "Consulting"]]}
    )
    frappe.db.delete(
        "Sales Stage",
        {
            "name": [
                "not in",
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
                    "Prospecting",
                ],
            ]
        },
    )
    frappe.db.commit()


def on_update_contact(doc, method=None):
    for d in doc.links:
        if d.link_doctype == "Lead":
            if not doc.department_cf:
                doc.department_cf = frappe.db.get_value(
                    "Lead", d.link_name, "department_cf"
                )
            if not doc.linkedin_profile_cf:
                doc.linkedin_profile_cf = frappe.db.get_value(
                    "Lead", d.link_name, "linkedin_profile_cf"
                )
            break


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def contact_for_customer_query(doctype, txt, searchfield, start, page_len, filters):
    """returns Contacts linked to Customer of filters.contact"""
    filters["txt"] = "%" + txt + "%"
    return frappe.db.sql(
        """select parent
             from 
                `tabDynamic Link` dl 
             where 
                dl.parenttype = 'Contact' and dl.link_doctype = 'Customer'
                and dl.link_name in (
                    select link_name 
                    from `tabDynamic Link` x 
                    where x.parenttype='Contact' and x.link_doctype = 'Customer'
                    and x.parent = %(contact)s
                )
                and parent like %(txt)s
                and parent <> %(contact)s""",
        filters,
        as_dict=False,
    )


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_contacts_for_customer(doctype, txt, searchfield, start, page_len, filters):

    filters["txt"] = "%%{}%%".format(txt)
    return frappe.db.sql(
        """
        select 
            distinct x.parent 
        from 
            `tabDynamic Link` x 
        where 
            x.parenttype='Contact' and x.link_doctype = 'Customer'
            and x.link_name = %(customer)s
            and x.parent like %(txt)s
    """,
        filters,
        as_dict=False,
    )


def create_event_for_interview(doc):
    """
    Create an Event,
    add interviewer if an Employee exists for that user
    """

    job_title = frappe.db.get_value("Job Opening", doc.job_opening, "job_title")
    subject = "Interview of {0} for {1} ({2})".format(
        doc.job_applicant, doc.job_opening, job_title
    )

    starts_on = get_datetime(
        "{0} {1}".format(getdate(doc.scheduled_on).strftime("%Y-%m-%d"), doc.from_time)
    )

    ends_on = get_datetime(
        "{0} {1}".format(getdate(doc.scheduled_on).strftime("%Y-%m-%d"), doc.to_time)
    )

    attendees = [d.interviewer for d in doc.interview_details]

    event = frappe.get_doc(
        {
            "doctype": "Event",
            "event_category": "Event",
            "subject": subject,
            "status": "Open",
            "starts_on": starts_on,
            "ends_on": ends_on,
            "event_type": "Private",
        }
    )
    for d in frappe.get_all("Employee", {"user_id": ["in", tuple(attendees)]}):
        event.append(
            "event_participants",
            dict(reference_doctype="Employee", reference_docname=d.name),
        )
    event.insert()


def attach_interview_ics(doc):
    file_name = "{}-interview.ics".format(doc.name)

    # remove existing ics attachment
    for d in get_attachments("Interview", doc.name):
        if d.file_name.startswith(file_name.replace(".ics", "")):
            frappe.delete_doc("File", d.name)

    doc.dtstart = format_datetime(
        get_datetime("{} {}".format(doc.scheduled_on, doc.from_time)),
        "YYYYMMDDThhmmss",
    )

    doc.dtend = format_datetime(
        get_datetime("{} {}".format(doc.scheduled_on, doc.to_time)),
        "YYYYMMDDThhmmss",
    )

    attendees = [frappe.db.get_value("Job Applicant", doc.job_applicant, "email_id")]
    for i in doc.interview_details:
        attendees.append(i.interviewer)
    doc.attendees = "\n".join(
        [
            f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=ACCEPTED:MAILTO:{x}"
            for x in attendees
        ]
    )
    ics_file = frappe.render_template("templates/includes/interview_ics.html", doc)
    # print(ics_file)

    _file = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": file_name,
            "attached_to_doctype": "Interview",
            "attached_to_name": doc.name,
            "folder": "Home/Attachments",
            "is_private": True,
            "content": ics_file,
        }
    )
    _file.save(ignore_permissions=True)


def on_update_interview(doc, method):
    try:
        create_event_for_interview(doc)
        attach_interview_ics(doc.as_dict())
    except:
        frappe.log_error(frappe.get_traceback())


def autoname_job_opening(doc, method):
    doc.name = make_autoname("JO-.YY.-.#")


def on_update_job_opening(doc, method):
    if doc.opportunity_cf and doc.opportunity_consulting_detail_ct_cf:
        # notify update to reload Opportunity in client
        opportunity = frappe.get_doc("Opportunity", doc.opportunity_cf)
        update = 0
        detail = [
            d
            for d in opportunity.opportunity_consulting_detail_ct_cf
            if d.name == doc.opportunity_consulting_detail_ct_cf
        ]
        for d in detail:
            d.job_opening = doc.name
            opportunity.save()


def on_update_job_applicant(doc, method):
    results = frappe.db.sql(
        """
        update `tabOpportunity Consulting Detail CT` ocd 
        inner join 
        (
            select 
            opportunity_consulting_stage , tja.job_title 
            from `tabOpportunity Job Applicant Status Priority Mapping` tmap 
            inner join `tabJob Applicant` tja on tja.status = tmap.job_applicant_status 
            where tja.job_title = %s
            order by priority 
            limit 1
        ) t1 on ocd.job_opening = t1.job_title 
        set ocd.stage = t1.opportunity_consulting_stage 
    """,
        (doc.job_title),
    )

    for d in frappe.get_all(
        "Job Opening", filters={"name": doc.job_title}, fields=["opportunity_cf"]
    ):
        if d.opportunity_cf:
            # notify so doc is reloaded in client
            frappe.get_doc("Opportunity", d.opportunity_cf).notify_update()


def notify_sales_stage_update(doc, method):
    """
    Trigger notification for when Stage is updated in Opportunity > opportunity_consulting_detail_ct_cf
    Has to be done in validation, because in on_update we will not know if stage value hsa changed
    """
    notification = frappe.db.get_single_value(
        "NPro Settings", "opportunity_consulting_detail_stage_update_notification"
    )

    if notification:
        for d in doc.opportunity_consulting_detail_ct_cf:
            old_value = frappe.db.get_value(
                "Opportunity Consulting Detail CT", d.name, "stage"
            )
            if not old_value == d.stage:
                doc.consulting_detail = d
                evaluate_alert(doc, notification, "Custom")


# def __on_update_job_applicant(doc, method):
#     new_stage = None
#     if doc.job_title:
#         for d in frappe.db.sql(
#             """
#             select name, stage
#             from `tabOpportunity Consulting Detail CT`
#             where job_opening = %s
#                 """,
#             (doc.job_title),
#             as_dict=True,
#         ):
#             stage = get_consulting_stage_for_applicant_status(doc.status, d.stage)
#             print(stage)

#             if stage:
#                 frappe.db.sql(
#                     """update `tabOpportunity Consulting Detail CT`
#                     set stage = %s where name = %s""",
#                     (stage, d.name),
#                 )


# def __get_consulting_stage_for_applicant_status(job_applicant_status, stage):
#     settings = frappe.get_single("NPro Settings")
#     priority_mapping = settings.opportunity_job_applicant_status_priority_mapping

#     _map = {x.opportunity_consulting_stage: x.priority for x in priority_mapping}
#     _temp = [
#         x for x in priority_mapping if x.job_applicant_status == job_applicant_status
#     ]

#     for t in _temp:
#         if not _map.get(stage) or t.priority < _map.get(stage):
#             return t.opportunity_consulting_stage

#     return stage
