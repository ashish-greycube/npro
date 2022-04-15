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
		report.show_footer_message = function (report) {
			this.$report_footer && this.$report_footer.remove();
			this.$report_footer = $(`<div class="report-footer text-muted"></div>`).appendTo(this.page.main);

			const message = __(`
			<table cellpadding="2">
			<tr>
				<th>Stage </th>
				<th>Status </th>
			</tr>
			<tr>
				<td>Applied</td>
				<td>Applied within selected dates.</td>
			</tr>
			<tr>
				<td>Passed NPro Screening</td>
				<td>'Rejected', 'Accepted', 'Hold', 'Interview Scheduled' or status like 'CV*'</td>
			</tr>
			<tr>
				<td>Selected By client</td>
				<td>CV Selected for Interview</td>
			</tr>
			<tr>
				<td>Rejected By client</td>
				<td>Rejected by Client</td>
			</tr>
			<tr>
				<td>CV Shared</td>
				<td>CV Shared with Client</td>
			</tr>
			<tr>
				<td>Selected</td>
				<td>Accepted</td>
			</tr>

		</table>

			`);
			const execution_time_msg = __('Execution Time: {0} sec', [this.execution_time || 0.1]);

			this.$report_footer.append(`<div class="col-md-12">
			<span">${message}</span><span class="pull-right">${execution_time_msg}</span>
		</div>`);
		}
	}


};
