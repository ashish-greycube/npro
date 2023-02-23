frappe.ui.form.on("Lead", {
  refresh: function (frm) {
    frm.dashboard.hide();
    if (!frm.is_new() && frm.doc.__onload && !frm.doc.__onload.is_customer) {
      frm.remove_custom_button("Opportunity", "Create");
      frm.remove_custom_button("Quotation", "Create");
    }
  },
  onload_post_render: function (frm) {
    frm.dashboard.hide();
    if (!frm.is_new() && frm.doc.__onload && !frm.doc.__onload.is_customer) {
      frm.remove_custom_button("Opportunity", "Create");
      frm.remove_custom_button("Quotation", "Create");
    }
  },

  years_of_experience_in_the_org_cf: function (frm) {
    frappe.utils.check_numeric("years_of_experience_in_the_org_cf", frm);
  },

  email_id: function (frm) {
    let email_id = frm.doc.email_id;
    if (
      email_id &&
      (!email_id.endsWith(".com") || email_id.indexOf("@") == -1)
    ) {
      frappe.throw(
        "Invalid Email ID. Valid Email Id should have '@' and end in '.com' "
      );
    }
  },
});
