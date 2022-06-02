// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Job Applicant Status"] = {
	"filters": [

	]
	,
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "applicant_name") {
			value = `<a href="/app/job-applicant/${data['applicant']}" data-doctype="Job Applicant">${data['applicant_name']}</a>`;
		}
		return value;
	},

};
