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
    frappe.utils.check_numeric("years_of_experience_in_the_org_cf", frm, true);
  },

  validate: function (frm) {
    frappe.utils.check_validate([
      [frappe.utils.check_numeric, "phone", frm],
      [frappe.utils.check_numeric, "mobile_no", frm],
      [frappe.utils.check_numeric, "years_of_experience_in_the_org_cf", frm],
      [frappe.utils.validate_email, "email_id", frm],
    ]);
  },
});
