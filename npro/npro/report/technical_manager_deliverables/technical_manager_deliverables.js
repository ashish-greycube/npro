// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Technical Manager Deliverables"] = {
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
    {
      "fieldname": "priority",
      "label": __("Priority"),
      "fieldtype": "Select",
      "options": ["", "Low", "Medium", "High", "Urgent"]
    },
    {
      "fieldname": "task_status",
      "label": __("Task Status"),
      "fieldtype": "Select",
      "options": ["", "Open", "Working", "Pending Review", "Overdue", "Completed"]
    },
  ],

  "formatter": function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);
    if (column.id == "delay") {
      if (data["delay"] > 0) {
        value = `<p style="color: red; font-weight: bold">${value}</p>`;
      } else {
        value = `<p style="color: green; font-weight: bold">${value}</p>`;
      }
    }
    return value
  },


  onload: function (report) {
    // report.page.set_title("");
  },
};
