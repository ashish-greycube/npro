// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Contactwise Communication Frequency Alert"] = {
  filters: [
    {
      fieldname: "account_manager",
      label: __("Account Manager"),
      fieldtype: "Link",
      options: "User",
    },
  ],

  onload: function (report) {
    report.page.set_title("Customer Contact Frequency");
  },
};
