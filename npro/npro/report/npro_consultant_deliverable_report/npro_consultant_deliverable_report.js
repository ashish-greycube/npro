// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["NPro Consultant Deliverable Report"] = {
  filters: [
    {
      fieldname: "project",
      label: __("Project"),
      fieldtype: "Link",
      options: "Project",
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
      fieldname: "candidate",
      label: __("Candidate"),
      fieldtype: "Data",
      // options: "Project",
      reqd: 0,
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
