// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer View of Opportunities"] = {
  filters: [
    {
      fieldname: "opportunity_owner",
      label: __("Opportunity Owner"),
      fieldtype: "Link",
      options: "User",
    },
    {
      fieldname: "opportunity_type",
      label: __("Opportunity Type"),
      fieldtype: "Link",
      options: "Opportunity Type",
    },
    {
      fieldname: "from_date",
      label: __("From Date (Opportunity Creation Date)"),
      fieldtype: "Date",
      default: moment().startOf("month"),
      reqd: 1,
    },
    {
      fieldname: "to_date",
      label: __("To Date (Opportunity Creation Date)"),
      fieldtype: "Date",
      default: moment(),
      reqd: 1,
    },
    {
      fieldname: "timespan",
      label: __("Lead Creation Date within "),
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
};
