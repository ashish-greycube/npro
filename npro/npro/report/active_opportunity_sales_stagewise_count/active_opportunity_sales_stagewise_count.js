// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Active Opportunity Sales Stagewise Count"] = {
  filters: [
    {
      fieldname: "status",
      label: __("Status"),
      fieldtype: "Select",
      options: " Open\nConverted\nLost",
    },

    {
      fieldname: "opportunity_owner",
      label: __("Sales Person"),
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

  onload: function (report) {},
};
