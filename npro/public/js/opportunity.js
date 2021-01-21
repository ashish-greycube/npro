frappe.ui.form.on("Opportunity", {
    status:function(frm){
        if (frm.doc.status=='Lost' && frm.doc.lost_reasons.length==0) {
            frm.trigger('set_as_lost_dialog');
        }        
    },
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