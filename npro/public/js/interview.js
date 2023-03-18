frappe.ui.form.on("Interview", {
  setup: function (frm) {
    setTimeout(() => {
      frm.trigger("set_interview_round_filter");
    }, 600);
  },

  refresh: function (frm) {
    setTimeout(() => {
      frm.page.remove_inner_button("Submit Feedback");
    }, 1);

    frm.trigger("add_custom_buttons");
  },

  add_custom_buttons: function (frm) {
    frm.add_custom_button(__("Interview Feedback"), function () {
      console.log("create feedback");
      let _doc = frappe.model.make_new_doc_and_get_name("Interview Feedback");
      _doc = locals["Interview Feedback"][_doc];

      $.extend(_doc, {
        interview: frm.doc.name,
        interview_round: frm.doc.interview_round,
        job_applicant: frm.doc.job_applicant,
        interviewer: frappe.user.name,
        interviewer_name_cf: frappe.user.full_name(),
      });

      frappe.set_route("Form", "Interview Feedback", _doc.name);
    });
  },

  set_interview_round_filter(frm) {
    frm.set_query("interview_round", function () {
      return {
        filters: {
          job_opening_cf: ["=", frm.doc.job_opening_cf],
        },
      };
    });
  },
});
