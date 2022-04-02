frappe.ui.form.on('Job Offer', {
    refresh: function (frm) {
        frm.events.set_exchange_rate(frm);
    },

    consultancy_fees_offered_cf: function (frm) {
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
                    if (frm.doc.consultancy_fees_offered_cf) {
                        frm.set_value('consultancy_fees_offered_usd_cf', (frm.doc.consultancy_fees_offered_cf || 0) * r.message)
                    }
                }
            }
        });
    }
});
