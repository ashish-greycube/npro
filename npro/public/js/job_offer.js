frappe.ui.form.on("Job Offer", {
  refresh: function (frm) {
    frm.events.add_custom_buttons(frm);
    frm.trigger("toggle_offer_approver");
  },

  status(frm) {
    if (!frm.doc.offer_approver_cf) {
      frm.set_value("offer_approver_cf", frappe.user.name);
    }
    // frm.trigger("toggle_offer_approver");
  },

  toggle_offer_approver(frm) {
    if (
      !frm.doc.offer_approver_cf ||
      frm.doc.offer_approver_cf == frappe.user.name
    ) {
      frm.set_df_property("offer_approver_cf", "disabled", 1);
    }
  },

  add_custom_buttons(frm) {
    frm.remove_custom_button("Create Employee");
    frm.remove_custom_button(__("Show Employee"));

    frm.add_custom_button(__("Create Consultant"), function () {
      frm.trigger("make_consultant");
    });

    if (
      !frm.doc.__islocal &&
      frm.doc.status == "Accepted" &&
      frm.doc.docstatus === 1 &&
      (!frm.doc.__onload || !frm.doc.__onload.employee)
    ) {
      frm.add_custom_button(__("Create Consultant"), function () {
        frm.trigger("make_consultant");
      });
    }

    if (frm.doc.__onload && frm.doc.__onload.employee) {
      frm.add_custom_button(__("Show Consultant"), function () {
        frappe.set_route("Form", "Employee", frm.doc.__onload.employee);
      });
    }
  },

  consultancy_fees_offered_cf: function (frm) {
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
            "consultancy_fees_offered_usd_cf",
            (frm.doc.consultancy_fees_offered_cf || 0) * r.message
          );
        }
      },
    });
  },

  make_consultant: function (frm) {
    frappe.model.open_mapped_doc({
      method: "npro.utils.make_consultant_from_job_offer",
      frm: frm,
    });
  },

  validate: function (frm) {
    if (frm.doc.status == "Sent for Approval") {
      if (frm.doc.offer_approver_cf !== frm.doc.offer_approved_by_cf) {
        frappe.throw(
          __("Offer in status 'Sent For Approval' cannot be changed ")
        );
      }
    }
  },
});
