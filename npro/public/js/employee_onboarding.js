frappe.ui.form.on("Employee Onboarding", {
  refresh: function (frm) {
    if (frm.doc.docstatus == 1) {
      setTimeout(() => {
        frm.page.set_secondary_action("Cancel", () => {
          show_rejection_reason_dialog(frm);
        });
      }, 300);
    }
  },

  cancel_onboarding: function (frm, reasons) {
    return frappe.call({
      method: "npro.npro.doc_events.cancel_consultant_onboarding",
      args: { name: frm.doc.name, rejection_reasons: reasons },
      callback: function (r) {
        frm.reload_doc();
      },
    });
  },
});

function show_rejection_reason_dialog(frm) {
  let d = new frappe.ui.Dialog({
    title: __("Select Rejection Reasons"),
    fields: [
      {
        label: "Rejection Reason",
        fieldname: "rejection_reason",
        fieldtype: "Table MultiSelect",
        reqd: 1,
        options: "Npro Rejected Reason Detail",
      },
    ],
    primary_action: function () {
      var data = d.get_values();
      // console.log(data);
      d.hide();
      frm.events.cancel_onboarding(frm, data.rejection_reason);
    },
    primary_action_label: __("Cancel Onboarding"),
  });
  d.show();
}
