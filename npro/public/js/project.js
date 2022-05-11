frappe.ui.form.on('Project', {
    // refresh: function (frm) {

    // },

    setup: function (frm) {
        frm.set_query("customer_contact_cf", function () {
            return {
                query: 'npro.utils.get_customer_contacts',
                filters: {
                    customer: frm.doc.customer
                }
            };
        });
    },

    customer_contact_cf: function (frm) {
        frappe.db.get_value("Contact", frm.doc.customer_contact_cf, ['first_name', 'last_name']).then(r => {
            frm.set_value("customer_reporting_mgr_cf", `${r.message.first_name || ''} ${r.message.last_name || ''}`.trim())
        })
    }
});
