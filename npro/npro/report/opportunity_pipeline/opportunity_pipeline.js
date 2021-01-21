// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Opportunity Pipeline"] = {
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
  ],
};
