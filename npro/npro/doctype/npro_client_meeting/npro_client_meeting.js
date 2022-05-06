// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('NPro Client Meeting', {
	// refresh: function (frm) {	}

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
