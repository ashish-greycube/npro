frappe.ui.form.on("Interview Round", {
  setup: function (frm) {
    frm.trigger("hide_grid_add_row");
  },
  hide_grid_add_row: function (frm) {
    setTimeout(() => {
      frm.fields_dict.expected_skill_set.grid.wrapper
        .find(".grid-add-row")
        .remove();
    }, 100);
  },
  //   job_opening_cf: function (frm) {
  //     frappe.model.with_doc("Job Opening", frm.doc.job_opening_cf).then(() => {
  //       let jo = frappe.get_doc("Job Opening", frm.doc.job_opening_cf);
  //       frm.doc.expected_skill_set = [];
  //       for (const d of jo.jrss_ct_cf) {
  //         frm.add_child("expected_skill_set", {
  //           skill: d.skill,
  //           expected_proficiency_cf: d.proficiency,
  //         });
  //       }
  //       frm.refresh_field("expected_skill_set");
  //       frm.trigger("hide_grid_add_row");
  //     });
  //   },
});
