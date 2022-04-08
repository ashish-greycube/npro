frappe.ui.form.on('Job Applicant', {
    refresh: function (frm) {
        if (frm.doc.docstatus == 0)
            frm.events.set_exchange_rate(frm);
    },

    current_salary_cf: function (frm) {
        frm.events.set_exchange_rate(frm);
    },


    set_exchange_rate: function (frm) {
        frappe.call({
            method: "erpnext.setup.utils.get_exchange_rate",
            args: {
                from_currency: "INR",
                to_currency: "USD"
            },
            callback: function (r) {
                if (r.message) {
                    frm.set_value('conversion_rate_cf', r.message)
                    if (frm.doc.current_salary_cf) {
                        frm.set_value('current_salary_usd_cf', (frm.doc.current_salary_cf || 0) * r.message)
                    }
                }
            }
        });
    },

});