// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Candidate Onboarded"] = {
  filters: [

    {
      fieldname: "timespan",
      label: __("Date of Joining in "),
      fieldtype: "Select",
      options: npro.utils.TIMESPAN_OPTIONS,
      on_change: function (query_report) {
        let date_range = npro.utils.get_date_range(
          query_report.get_values().timespan
        );
        frappe.query_report.set_filter_value({
          from_date: date_range[0],
          till_date: date_range[1],
        });
      },
      default: "This Month",
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: moment().startOf("month"),
      reqd: 1,
    },
    {
      fieldname: "till_date",
      label: __("Till Date"),
      fieldtype: "Date",
      default: moment(),
      reqd: 1,
    },
  ],

  "formatter": function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);

    if (column.fieldname == "employee_name") {
      value = `<a href="/app/employee/${data['employee']}" data-doctype="Employee">${data['employee_name']}</a>`;
    } else if (column.fieldname == "job_title") {
      value = `<a href="/app/job-opening/${data['job_name']}" data-doctype="Job Opening">${data['job_title']}</a>`;
    }


    return value;
  },


  onload: function (report) {
    // report.page.set_title("");
  },
};
