// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Job Opening Ageing Analysis"] = {
  filters: [
    {
      fieldname: "npro_sourcing_owner_cf",
      label: __("NPro Sourcing Owner"),
      fieldtype: "Link",
      options: "User",
    },
    {
      fieldname: "customer_cf",
      label: __("Customer"),
      fieldtype: "Link",
      options: "Customer",
    },
    {
      fieldname: "from_date",
      label: __("From Date (Opportunity Creation Date)"),
      fieldtype: "Date",
      default: moment().startOf("year"),
      reqd: 1,
    },
    {
      fieldname: "till_date",
      label: __("Till Date (Opportunity Creation Date)"),
      fieldtype: "Date",
      default: frappe.datetime.get_today(),
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
    // report.page.set_title("Active Opportunity Ageing By Status");s
  },
};
