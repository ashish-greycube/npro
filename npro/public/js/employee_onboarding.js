frappe.ui.form.on("Employee Onboarding", {
  refresh: function (frm) {
    if (frm.doc.docstatus == 1) {
      setTimeout(() => {
        frm.page.set_secondary_action("Cancel", () => {
          return frappe.call({
            method: "npro.npro.doc_events.cancel_consultant_onboarding",
            args: { name: frm.doc.name },
            callback: function (r) {
              frm.reload_doc();
            },
          });
        });
      }, 300);
    }
  },
});
