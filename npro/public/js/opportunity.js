frappe.ui.form.on("Opportunity", {
    setup:function(frm)
    {
        frm.set_query('sales_stage', () => {
        return {
            filters: {
                opportunity_type_cf: ['in', [frm.doc.opportunity_type,""]]
            }
        }
    })
    },
	refresh: function(frm) {
        frm.set_value('opportunity_from','Customer',true)

    }
})