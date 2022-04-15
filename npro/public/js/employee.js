frappe.ui.form.on("Employee", {
    refresh: function (frm) {
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
    let row = frappe.get_doc(cdt, cdn);
    frappe.call({
        method: "erpnext.setup.utils.get_exchange_rate",
        args: {
            from_currency: "INR",
            to_currency: "USD",
            transaction_date: frm.doc.date_of_joining
        },
        callback: function (r) {
            if (r.message) {
                row.amount_in_usd = (row.amount_in_inr || 0) * r.message;
                refresh_field("amount_in_usd", row.name, row.parentfield);
            }
        }
    });

}