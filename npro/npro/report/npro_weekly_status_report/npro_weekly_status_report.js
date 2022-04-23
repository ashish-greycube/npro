// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["NPro Weekly Status Report"] = {
  filters: [

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
