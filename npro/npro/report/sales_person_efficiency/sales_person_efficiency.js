// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Person Efficiency"] = {
  filters: [
    {
      fieldname: "organization",
      label: __("Organization"),
      fieldtype: "Select",
    },
  ],

  get_options: function () {
    return ["SAAB"];
  },

  onload: function () {
    return frappe.call({
      method:
        "npro.npro.report.sales_person_efficiency.sales_person_efficiency.get_organizations",
      callback: function (r) {
        var org_filter = frappe.query_report.get_filter("organization");
        org_filter.df.options = r.message;
        org_filter.refresh();
      },
    });
  },
};
