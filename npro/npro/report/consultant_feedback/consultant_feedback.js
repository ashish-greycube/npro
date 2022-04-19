// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Consultant Feedback"] = {
  filters: [

  ],

  "formatter": function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);

    if (column.fieldname == "employee_name") {
      value = `<a href="/app/employee/${data['employee']}" data-doctype="Employee">${data['employee']}</a>`;
    } else if (column.fieldname == "job_title") {
      value = `<a href="/app/job-opening/${data['job_name']}" data-doctype="Job Opening">${data['job_title']}</a>`;
    }

    return value;
  },


  onload: function (report) {
    // report.page.set_title("");
  },
};
