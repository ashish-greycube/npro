// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Project Tasks Report"] = {
  filters: [
    {
      fieldname: "project_type",
      label: __("Project Type"),
      fieldtype: "Link",
      options: "Project Type",
    },
    {
      fieldname: "project",
      label: __("Project"),
      fieldtype: "Link",
      options: "Project",
      "get_query": () => {
        return {
          filters: {
            "project_type": frappe.query_report.get_filter_value('project_type')
          }
        }
      }
    },
    {
      "fieldname": "from_date",
      "label": __("From Date (Task Created On)"),
      "fieldtype": "Date",
      "default": frappe.datetime.month_start(),
    },
    {
      "fieldname": "to_date",
      "label": __("To Date (Task Created On)"),
      "fieldtype": "Date",
      "default": frappe.datetime.get_today(),
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
    } else if (column.fieldname == "project") {
      value = `<a href="/app/project/${data['project']}" data-doctype="Project">${data['project']}</a>`;
    }
    return value;
  },


  onload: function (report) {
  },
};
