// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Lead Status Reminder"] = {
  filters: [
    {
      fieldname: "lead_owner",
      label: __("Lead Owner"),
      fieldtype: "Link",
      options: "User",
    },
  ],
};
