// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Leads By Status Owner"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date (Lead Creation Date)"),
      fieldtype: "Date",
      default: moment().startOf("month").subtract(3, "months"),
    },
    {
      fieldname: "to_date",
      label: __("To Date (Lead Creation Date)"),
      fieldtype: "Date",
      default: frappe.datetime.get_today(),
    },
    {
      fieldname: "timespan",
      label: __("Lead Creation Date in "),
      fieldtype: "Select",
      options: npro.utils.TIMESPAN_OPTIONS,
      on_change: function (query_report) {
        let date_range = npro.utils.get_date_range(
          query_report.get_values().timespan
        );
        frappe.query_report.set_filter_value({
          from_date: date_range[0],
          to_date: date_range[1],
        });
      },
      default: "This Month",
    },
  ],

  _after_datatable_render: function (datatable) {
    const chart_columns = {
      New: "#fff168",
      Working: "#aee4ff",
      Nurturing: "#9deca2",
      Converted: "#49937E",
      "Do Not Contact": "#ff4d4d",
    };
    npro.utils.create_chart(
      "lead_owner",
      chart_columns,
      datatable,
      frappe.query_report
    );
  },
};
