// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Active Opportunity Ageing Analysis by Activity"] = {
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
      label: __("From Date (Sales Stage Last Updated Date)"),
      fieldtype: "Date",
      default: moment().startOf("year"),
      reqd: 1,
    },
    {
      fieldname: "till_date",
      label: __("Till Date (Sales Stage Last Updated Date)"),
      fieldtype: "Date",
      default: moment(),
      reqd: 1,
    },
    {
      fieldname: "range1",
      label: __("Ageing Range 1"),
      fieldtype: "Int",
      default: "30",
      reqd: 1,
    },
    {
      fieldname: "range2",
      label: __("Ageing Range 2"),
      fieldtype: "Int",
      default: "60",
      reqd: 1,
    },
    {
      fieldname: "range3",
      label: __("Ageing Range 3"),
      fieldtype: "Int",
      default: "90",
      reqd: 1,
    },
  ],

  onload: function (report) {
    report.page.set_title("Active Opportunity Ageing By Activity");
  },
};
