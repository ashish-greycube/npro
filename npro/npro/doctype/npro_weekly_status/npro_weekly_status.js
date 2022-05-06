// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('NPro Weekly Status', {
	week_start_date: function (frm) {
		frm.set_value('week_end_date', frappe.datetime.add_days(frm.doc.week_start_date, 6));
	},
	setup: function (frm) {
		frm.set_query('project', () => {
			return {
				filters: {
					project_type: ['in', ["Internal"]]
				}
			}
		})
	},

});
