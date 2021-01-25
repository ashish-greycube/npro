frappe.ui.form.on("Contact", {
  setup: function (frm) {
    frm.set_query("reports_to_cf", () => {
      return {
        query: "npro.api.contact_for_customer_query",
        filters: { contact: frm.doc.name },
      };
    });
  },

  refresh: function (frm) {},
});
