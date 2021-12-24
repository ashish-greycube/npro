// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Job Applicant Analysis"] = {
	"filters": [
		{
			fieldname: "job_opening",
			label: __("Job Opening"),
			fieldtype: "Link",
			options: "Job Opening",
		},
		{
			fieldname: "interviewer",
			label: __("Interviewer"),
			fieldtype: "Select",
		},
	],
	"onload": function () {
		return frappe.call({
			method: "npro.npro.report.job_applicant_analysis.job_applicant_analysis.get_interviewers",
			callback: function (r) {
				console.log(r);
				var filter = frappe.query_report.get_filter('interviewer');
				filter.df.options = r.message.join("\n");
				filter.refresh();
			}
		});
	}
};

