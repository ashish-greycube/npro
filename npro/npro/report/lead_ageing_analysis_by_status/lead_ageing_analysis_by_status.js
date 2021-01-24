// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Lead Ageing Analysis By Status"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: frappe.datetime.get_today(),
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
    {
      fieldname: "till_date",
      label: __("Till Date"),
      fieldtype: "Date",
      default: moment().startOf("year"),
    },
  ],
};
