frappe.ui.form.on('Lead', {
	refresh: function (frm) {
        frm.dashboard.hide()
		if (!frm.is_new() && frm.doc.__onload && !frm.doc.__onload.is_customer) {
            frm.remove_custom_button('Opportunity','Create')
            frm.remove_custom_button('Quotation','Create')
		}

    },
	onload_post_render: function (frm) {
        frm.dashboard.hide()
		if (!frm.is_new() && frm.doc.__onload && !frm.doc.__onload.is_customer) {
            frm.remove_custom_button('Opportunity','Create')
            frm.remove_custom_button('Quotation','Create')
		}

	}    
});
