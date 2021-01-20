frappe.ui.form.on("Opportunity", {
	refresh: function(frm) {
        frm.set_value('opportunity_from','Customer',true)

    }
})