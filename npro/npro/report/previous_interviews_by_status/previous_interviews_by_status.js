// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Previous Interviews by Status"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("Interview From Date"),
      fieldtype: "Date",
      default: moment().startOf("month"),
      reqd: 1,
    },
    {
      fieldname: "till_date",
      label: __("Interview Till Date"),
      fieldtype: "Date",
      default: moment(),
      reqd: 1,
    },
    {
      fieldname: "timespan",
      label: __("Interview Date in"),
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
      default: "This Month",
    },
  ],

  onload: function (report) {
    // report.page.set_title("");
  },
};
