// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Post Onboarding Activities"] = {
  filters: [
    {
      fieldname: "job_applicant",
      label: __("Candidate"),
      fieldtype: "Link",
      options: "Job Applicant"
    },
    {
      fieldname: "customer",
      label: __("Client"),
      fieldtype: "Link",
      options: "Customer"
    },
    {
      fieldname: "task_status",
      label: __("Task Status"),
      fieldtype: "Select",
      options: "\nOpen\nWorking\nPending Review\nOverdue\nTemplate\nCompleted\nCancelled "
    },
    {
      fieldname: "post_boarding_status",
      label: __("Post Boarding Status"),
      fieldtype: "Select",
      options: "\nPending\nIn Process\nCompleted"
    },

  ],

  "formatter": function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);

    if (column.fieldname == "employee_name") {
      value = `<a href="/app/employee/${data['employee']}" data-doctype="Employee">${data['employee_name']}</a>`;
    } else if (column.fieldname == "subject") {
      value = `<a href="/app/task/${data['task_name']}" data-doctype="Task">${data['subject']}</a>`;
    }
    return value;
  },


  onload: function (report) {
  },
};
