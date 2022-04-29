frappe.ui.form.on("Employee", {
    refresh: function (frm) {
    },

    conversion_rate_cf: function (frm) {
        for (const d of frm.doc.npro_consultant_other_cost_cf || []) {
            set_amount_in_usd(frm, d.doctype, d.name)
        }
    },

});

frappe.ui.form.on("Npro Consultant Other Cost", {
    amount_in_inr: function (frm, cdt, cdn) {
        set_amount_in_usd(frm, cdt, cdn);
    },

    cost_type: function (frm, cdt, cdn) {
        set_amount_in_usd(frm, cdt, cdn);
    },

});

function set_amount_in_usd(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn), conversion_rate = frm.doc.conversion_rate_cf;
    if (conversion_rate) {
        row.amount_in_usd = (row.amount_in_inr || 0) * conversion_rate;
        refresh_field("amount_in_usd", row.name, row.parentfield);
    }

    // frappe.call({
    //     method: "erpnext.setup.utils.get_exchange_rate",
    //     args: {
    //         from_currency: "INR",
    //         to_currency: "USD",
    //         transaction_date: frm.doc.date_of_joining
    //     },
    //     callback: function (r) {
    //         if (r.message) {
    //             row.amount_in_usd = (row.amount_in_inr || 0) * r.message;
    //             refresh_field("amount_in_usd", row.name, row.parentfield);
    //         }
    //     }
    // });

}