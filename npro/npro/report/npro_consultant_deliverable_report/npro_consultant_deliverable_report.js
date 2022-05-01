// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["NPro Consultant Deliverable Report"] = {
  filters: [
    {
      fieldname: "candidate",
      label: __("Consultant"),
      fieldtype: "Link",
      options: "Employee",
      reqd: 0,
    },
    {
      fieldname: "client",
      label: __("Client"),
      fieldtype: "Link",
      options: "Customer",
      reqd: 0,
    },
    {
      fieldname: "project",
      label: __("Project"),
      fieldtype: "Link",
      options: "Project",
      reqd: 0,
    },
    {
      fieldname: "from_date",
      label: __("From Date (Timesheet Detail From Time)"),
      fieldtype: "Date",
      default: moment().startOf("month"),
      reqd: 1,
    },
    {
      fieldname: "till_date",
      label: __("Till Date (Timesheet Detail From Time)"),
      fieldtype: "Date",
      default: moment(),
      reqd: 1,
    },
  ],

  "formatter": function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);

    if (column.fieldname == "subject") {
      if (data['task'])
        value = `<a href="/app/task/${data['task']}" data-doctype="Task">${data['subject']}</a>`;
    } else if (column.fieldname == "employee_name") {
      value = `<a href="/app/employee/${data['employee']}" data-doctype="Employee">${data['employee_name']}</a>`;
    } else if (column.fieldname == "project_name") {
      value = `<a href="/app/project/${data['project']}" data-doctype="Project">${data['project_name']}</a>`;
    } else if (column.fieldname == "hours") {
      value = `<div style='text-align: right'>${data['hours']}</div>`;
    }

    return value;
  },


  onload: function (report) {
  },
};
