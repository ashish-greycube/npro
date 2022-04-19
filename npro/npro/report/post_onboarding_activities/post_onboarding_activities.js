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

  ],

  "formatter": function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);

    if (column.fieldname == "job_applicant") {
      value = `<a href="/app/job-applicant/${data['job_applicant']}" data-doctype="Job Applicant">${data['employee_name']}</a>`;
    } else if (column.fieldname == "job_title") {
      value = `<a href="/app/job-opening/${data['job_name']}" data-doctype="Job Opening">${data['job_title']}</a>`;
    }
    return value;
  },


  onload: function (report) {
  },
};
