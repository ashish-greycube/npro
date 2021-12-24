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
	],
};
