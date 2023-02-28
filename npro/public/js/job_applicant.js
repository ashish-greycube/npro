frappe.ui.form.on("Job Applicant", {
  refresh: function (frm) {
    frm.events.toggle_create_interview(frm);

    if (!(frm.doc.__onload && frm.doc.__onload.job_offer)) {
      setTimeout(() => {
        frm.page.remove_inner_button("Job Offer");
        frm.add_custom_button(__("Job Offer"), function () {
          frappe.db
            .get_value("Job Opening", frm.doc.job_title, "billing_per_month_cf")
            .then((r) => {
              let billing = (r.message && r.message.billing_per_month_cf) || 0;
              console.log(billing);
              frappe.new_doc(
                "Job Offer",
                {
                  job_applicant: frm.doc.name,
                  applicant_name: frm.doc.applicant_name,
                  designation: frm.doc.job_opening,
                },
                function (doc) {
                  // non link values are not set in above, so set in callback
                  frappe.model.set_value(
                    doc.doctype,
                    doc.name,
                    "billing_per_month_cf",
                    billing
                  );
                }
              );
            });
        });
      }, 500);
    }
  },

  current_salary_cf: function (frm) {
    frm.events.set_exchange_rate(frm);
  },

  set_exchange_rate: function (frm) {
    frappe.call({
      method: "erpnext.setup.utils.get_exchange_rate",
      args: {
        from_currency: "INR",
        to_currency: "USD",
        transaction_date: frm.doc.creation,
      },
      callback: function (r) {
        if (r.message) {
          frm.set_value("conversion_rate_cf", r.message);
          frm.set_value(
            "current_salary_usd_cf",
            (frm.doc.current_salary_cf || 0) * r.message
          );
        }
      },
    });
  },

  validate: function (frm) {
    frappe.utils.check_validate([
      [frappe.utils.check_numeric, "phone_number", frm],
      [frappe.utils.validate_email, "email_id", frm],
    ]);
  },

  toggle_create_interview: function (frm) {
    let recording = (frm.doc.candidate_call_detail_cf || []).filter(
      (d) => d.call_type === "Screening Call"
    );

    if (!recording.length || !frm.doc.resume_attachment) {
      frm.custom_buttons["Create Interview"].prop("disabled", true);
    } else {
      frm.custom_buttons["Create Interview"].prop("disabled", false);
    }
  },
});
