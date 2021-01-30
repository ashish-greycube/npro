// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Contactwise Communication Analysis"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: moment().startOf("year"),
      reqd: 1,
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      default: moment(),
      reqd: 1,
    },
    {
      fieldname: "communication_medium",
      label: __("Event Category"),
      fieldtype: "Select",
      options: "\nEmail\nPhone\nMeeting\nOther",
    },
  ],

  onload: function (report) {
    report.page.set_title("Customer Communication Analysis");
  },

  _after_datatable_render: function (datatable) {
    const chart_columns = {
      Email: "#fff168",
      Meeting: "#a6e4ff",
      Total: "#9deca2",
      days_since_last_communication: "#49937E",
    };
    npro.utils.create_chart(
      "contact",
      chart_columns,
      datatable,
      frappe.query_report
    );
  },
};
