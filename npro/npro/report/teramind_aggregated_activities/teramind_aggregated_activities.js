// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Teramind Aggregated Activities"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: moment().startOf("week"),
      reqd: 1,
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      default: moment(),
      reqd: 1,
    },

  ],

  "formatter": function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);

    if (column.fieldname == "employee_name") {
      value = `<a target="_blank" href="/app/employee/${data['employee']}" data-doctype="Employee">${data['employee_name']}</a>`;
    }
    return value;
  },


  onload: function (report) {
    // report.page.set_title("");
  },
};
