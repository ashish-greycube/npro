frappe.ui.form.on('Job Applicant', {
    refresh: function (frm) {

    },

    current_salary_cf: function (frm) {
        frm.events.set_exchange_rate(frm);
    },


    set_exchange_rate: function (frm) {
        frappe.call({
            method: "erpnext.setup.utils.get_exchange_rate",
            args: {
                from_currency: "INR",
                to_currency: "USD",
                transaction_date: frm.doc.creation
            },
            callback: function (r) {
                if (r.message) {
                    frm.set_value('conversion_rate_cf', r.message)
                    frm.set_value('current_salary_usd_cf', (frm.doc.current_salary_cf || 0) * r.message)
                }
            }
        });
    },

});