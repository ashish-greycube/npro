frappe.ui.form.on("Job Opening", {
  refresh: function (frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__("Create Interview Round"), () => {
        let round_name = make_interview_round(frm);
        frappe.set_route("Form", "Interview Round", round_name);
      });
    }
  },

  customer_cf: function (frm) {
    frm.set_query("customer_contact_cf", function (doc) {
      return {
        query: "npro.api.get_contacts_for_customer",
        filters: { customer: frm.doc.customer_cf },
      };
    });
  },

  designation: function (frm) {
    if (frm.doc.designation) {
      frappe.model.with_doc("Designation", frm.doc.designation, () => {
        let designation = frappe.model.get_doc(
          "Designation",
          frm.doc.designation
        );
        let skills = (frm.doc.jrss_ct_cf || []).map((t) => t.skill);
        designation.skills.forEach((d) => {
          if (!skills.includes(d.skill)) {
            let row = frappe.model.add_child(frm.doc, "JRSS CT", "jrss_ct_cf");
            row.skill = d.skill;
            row.description = d.skill;
          }
        });
        frm.refresh_field("jrss_ct_cf");
      });
    }
  },
});

function make_interview_round(frm) {
  let doc_name = frappe.model.make_new_doc_and_get_name("Interview Round"),
    doc = locals["Interview Round"][doc_name];
  doc.job_opening_cf = frm.doc.name;
  doc.round_name = `${frm.doc.job_title}`;
  doc.designation = frm.doc.designation;
  let avg_proficiency = 0;
  (frm.doc.jrss_ct_cf || []).forEach((t) => {
    let skill = frappe.model.add_child(
      doc,
      "Expected Skill Set",
      "expected_skill_set"
    );
    skill.skill = t.skill;
    skill.description = t.description;
    skill.expected_proficiency_cf = t.proficiency || 0;
    avg_proficiency = avg_proficiency + (t.proficiency || 0);
  });
  if (avg_proficiency > 0) {
    doc.expected_average_rating = avg_proficiency / frm.doc.jrss_ct_cf.length;
  }
  return doc.name;
}
