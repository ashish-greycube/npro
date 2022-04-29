// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["NPro Weekly Status Report"] = {
  filters: [
    {
      fieldname: "timespan",
      label: __("Month Start/End Date"),
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
      default: "This Week",
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: moment().startOf("week"),
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

    if (column.fieldname == "subject") {
      value = `<a href="/app/task/${data['task_name']}" data-doctype="Task">${data['subject']}</a>`;
    } else if (column.fieldname == "parent_subject") {
      if (data['parent_task']) {
        value = `<a href="/app/task/${data['parent_task']}" data-doctype="Task">${data['parent_subject']}</a>`;
      }
    } else if (column.fieldname == "project_name") {
      value = `<a href="/app/project/${data['project']}" data-doctype="Project">${data['project_name']}</a>`;
    }

    return value;
  },


  onload: function (report) {
  },
};
