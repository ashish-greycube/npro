// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Opportunity Sales Stage Reminder"] = {
  filters: [
    {
      fieldname: "opportunity_owner",
      label: __("Owner"),
      fieldtype: "Link",
      options: "User",
    },
  ],
};
