// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Npro Monthly Status', {
	month_start_date: function (frm) {
		let end_date = moment(frm.doc.month_start_date).endOf('month').format();
		frm.set_value('month_end_date', end_date)
	}

});
