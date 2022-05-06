frappe.ui.form.on('Project', {
    refresh: function (frm) {

    },

    customer_contact_cf: function (frm) {
        frappe.db.get_value("Contact", frm.doc.customer_contact_cf, ['first_name', 'last_name']).then(r => {
            frm.set_value("customer_reporting_mgr_cf", `${r.message.first_name} ${r.message.last_name}`.trim())
        })
    }
});
