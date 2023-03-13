frappe.listview_settings["Job Applicant"] =
  frappe.listview_settings["Job Applicant"] || {};

$.extend(frappe.listview_settings["Job Applicant"], {
  hide_name_column: true,

  onload: function (listview) {
    listview.page.add_action_item(__("Email CV to Customer"), function () {
      email_cv_to_customer(listview);
    });
  },
});

const email_cv_to_customer = function (listview) {
  let selected_applicants = listview.get_checked_items(true);

  if (!selected_applicants && selected_applicants.length) {
    frappe.throw(__("Please select the job applicants to send resumes."));
  }

  frappe.call({
    method: "npro.utils.get_resumes",
    args: {
      applicants: selected_applicants,
    },
    callback: function (r) {
      if (r.message) {
        let email_composer = new frappe.views.CommunicationComposer({
          recipients: "",
          attach_document_print: false,
          email_template: r.message.email_template,
          success: function () {
            frappe.show_alert(__("CVs sent to client successfully."));
            set_status_client_cv_screening(selected_applicants);
          },
        });

        for (const att of r.message["resumes"]) {
          frappe.model.with_doc("File", att, function (r) {
            let resume = frappe.model.get_doc("File", att);
            email_composer.render_attachment_rows(resume);
          });
        }

        setTimeout(() => {
          email_composer.dialog.set_values({
            recipients: r.message.recipients,
          });
          email_composer.dialog.set_values({
            email_template: r.message.email_template,
          });
        }, 300);
      }
    },
  });
};

function set_status_client_cv_screening(applicants) {
  frappe.call({
    method: "npro.utils.update_job_applicant_status_client_cv_screening",
    args: {
      applicants: selected_applicants,
    },
  });
}
