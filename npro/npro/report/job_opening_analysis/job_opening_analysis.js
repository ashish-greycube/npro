// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Job Opening Analysis"] = {
	"filters": [
		{
			fieldname: "job_opening",
			label: __("Job Opening"),
			fieldtype: "Link",
			options: "Job Opening",
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
			get_query: function () {
				return {
					query: "npro.npro.report.job_opening_analysis.job_opening_analysis.get_customers",
				};
			}
		},
		{
			fieldname: "timespan",
			label: __("Lead Creation Date within "),
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
			default: "This Month",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			// default: moment().startOf("year"),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			// default: moment(),
			reqd: 1,
		},
	],
	onload: function (report) {
		report.get_filter('timespan').onchange();
	}
};
