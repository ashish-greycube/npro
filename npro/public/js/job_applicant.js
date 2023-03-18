frappe.ui.form.on("Job Applicant", {
  refresh: function (frm) {
    frm.trigger("toggle_create_interview");
    frm.trigger("setup_create_interview");

    if (!(frm.doc.__onload && frm.doc.__onload.job_offer)) {
      setTimeout(() => {
        frm.page.remove_inner_button("Job Offer");
        frm.add_custom_button(__("Job Offer"), () => {
          frm.trigger("make_offer");
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
    let btn = frm.custom_buttons["Create Interview"];
    if (!btn) return;

    frappe.db
      .get_single_value("NPro Settings", "screening_call_type")
      .then((screening_call_type) => {
        let recording = (frm.doc.candidate_call_detail_cf || []).filter(
          (d) => d.call_type === screening_call_type
        );
        btn.prop("disabled", !recording.length || !frm.doc.resume_attachment);
      });
  },

  setup_create_interview: function (frm) {
    // frm.custom_buttons["Create Interview"].prop("hidden", true);
    let btn = frm.custom_buttons["Create Interview"];
    if (!btn) return;
    btn.off("click").on("click", function (e) {
      frappe.db
        .get_list("Interview Round", {
          filters: {
            designation: frm.doc.designation,
            job_opening_cf: frm.doc.job_title,
          },
          fields: ["name", "interview_type"],
        })
        .then((res) => {
          let interview = frappe.model.make_new_doc_and_get_name("Interview");
          interview = locals["Interview"][interview];
          if (res.length) {
            interview.interview_round = res[0].name;
            interview.interview_type = res[0].interview_type;
          }
          interview.job_applicant = frm.doc.name;
          interview.status = "Pending";
          interview.job_opening_cf = frm.doc.job_title;
          frappe.set_route("Form", "Interview", interview.name);
        });
    });
    return;
  },

  make_offer: function (frm) {
    frappe.model.open_mapped_doc({
      method: "npro.utils.open_mapped_doc_job_offer",
      frm: frm,
    });

    // frappe.db.get_doc("NPro Settings").then((doc) => {
    //   console.log(doc);
    // });
    return;

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
  },
});
