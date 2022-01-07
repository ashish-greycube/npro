// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Closed Candidate Sourcing"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date (Job Creation Date)"),
			fieldtype: "Date",
			default: moment().startOf("year").format(),
		},
		{
			fieldname: "to_date",
			label: __("To Date (Job Creation Date)"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "timespan",
			label: __("Job Creation Date in "),
			fieldtype: "Select",
			options: npro.utils.TIMESPAN_OPTIONS,
			on_change: function (query_report) {
				let date_range = npro.utils.get_date_range(
					query_report.get_values().timespan
				);
				frappe.query_report.set_filter_value({
					from_date: date_range[0],
					to_date: date_range[1],
				});
			},
			default: "This Year",
		},
	]
};
