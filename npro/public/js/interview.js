frappe.ui.form.on("Interview", {
  onload: function (frm) {
    frm.trigger("set_interview_round_filter");
  },
  refresh: function (frm) {
    setTimeout(() => {
      frm.page.remove_inner_button("Submit Feedback");
    }, 1);
  },

  set_interview_round_filter(frm) {
    frm.set_query("interview_round", function () {
      return {
        filters: {
          job_opening_cf: ["=", frm.doc.job_opening],
        },
      };
    });
  },
});
