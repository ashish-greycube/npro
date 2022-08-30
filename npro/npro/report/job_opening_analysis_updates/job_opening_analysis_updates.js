// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Job Opening Analysis Updates"] = {
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
		{
			fieldname: "ignore_duration",
			label: __("Ignore Duration"),
			fieldtype: "Check",
			default: 1
		},
		{
			fieldname: "legend",
			fieldtype: "Button",
			label: "Show Stage Status Mapping",
			onclick: function () {
				show_legend();
			}
		}
	],
	onload: function (report) {
		report.get_filter('timespan').onchange();
	}

	// , "formatter": function (value, row, column, data, default_formatter) {
	// 	value = default_formatter(value, row, column, data);
	// 	if (column.fieldname == "job_opening") {
	// 		value = `<a href="/app/job-opening/${data['job_opening']}" data-doctype="Job Opening">${data['job_opening']}:${data['job_title']}</a>`;
	// 	}
	// 	return value
	// }

};

const legend = [
	{
		stage: "Candidates Applied",
		description: "Screening Call,Screening Call- Rejected,Technical interview,Technical interview- Rejected,Client CV Screening,Client CV Screening- Accepted,Client CV Screening- Rejected,Client Interview,Client interview-Rejected,Client Interview-rescheduled,Client Interview-waiting for feedback,Rejected by candidate,Hold,Accepted"
	},
	{
		stage: "Candidates Passed NPro Screening",
		description: "Technical interview,Technical interview- Rejected,Client CV Screening,Client CV Screening- Accepted,Client CV Screening- Rejected,Client Interview,Client interview-Rejected,Client Interview-rescheduled,Client Interview-waiting for feedback,Rejected by candidate,Hold,Accepted"
	},
	{
		stage: "Candidate passed Npro technical interview",
		description: "Client CV Screening,Client CV Screening- Accepted,Client CV Screening- Rejected,Client Interview,Client interview-Rejected,Client Interview-rescheduled,Client Interview-waiting for feedback,Rejected by candidate,Hold,Accepted"
	},
	{
		stage: "No Of CV Shared",
		description: "Client CV Screening,Client CV Screening- Accepted,Client CV Screening- Rejected,Client Interview,Client interview-Rejected,Client Interview-rescheduled,Client Interview-waiting for feedback,Rejected by candidate,Hold,Accepted"
	},
	{ stage: "CV accepted by Client", description: "Client CV Screening- Accepted, Client Interview, Client interview-Rejected, Client Interview-rescheduled, Client Interview-waiting for feedback, Rejected by candidate, Hold, Accepted" },
	{ stage: "CV rejected by Client", description: "Client CV Screening- Rejected" },
	{ stage: "Client Interview held", description: "Client interview-Rejected,Client Interview-waiting for feedback,Accepted,Hold" },
	{ stage: "Client interview-Rejected", description: "Client interview-Rejected" },
	{ stage: "Rejected by Candidate", description: "Rejected by Candidate" },

	{ stage: "Selected", description: "Accepted" },
]

function show_legend() {
	const dialog = new frappe.ui.Dialog({
		title: __("Stagewise Status"),
		fields: [
			{
				fieldname: "stage_legend",
				fieldtype: "HTML",
			}
		],
	});

	let html = frappe.render_template(`
	<table class="table">
		<thead>
			<th>Stage</th>
			<th>Status Included</th>
		</thead>
		{% for(var i=0, l=data.length; i<l; i++) { %}
			<tr>
				<td>{{data[i].stage}}</td>
				<td>{{data[i].description}}</td>
			</tr>
		{% } %}
	</table>`, { data: legend });
	dialog.get_field("stage_legend").$wrapper.append(html);
	dialog.show();
}