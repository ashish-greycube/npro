// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('NPro Timesheet', {


	fetch_dates: function (frm) {
		let existing_dates = frm.doc.npro_timesheet_detail.map(d => d.timesheet_date)
		return frappe.db.get_single_value('NPro Settings', 'default_timesheet_status').then((status) => {
			for (let d = 0; d < frappe.datetime.get_day_diff(frm.doc.to_date, frm.doc.frm_date); d++) {
				let dt = frappe.datetime.add_days(frm.doc.frm_date, d)
				if (!existing_dates.includes(dt)) {
					let child = frm.add_child('npro_timesheet_detail')
					child.status = status;
					child.timesheet_date = dt;
				}
			}
			frm.refresh_field("npro_timesheet_detail")
		})

	}
});
