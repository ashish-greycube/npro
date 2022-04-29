// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Npro Client Weekly Status', {
	// refresh: function(frm) {

	// }

	week_start_date: function (frm) {
		frm.set_value('week_end_date', frappe.datetime.add_days(frm.doc.week_start_date, 6));
	}

});
