// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Active Lead Ageing Analysis By Rep"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date (Lead Creation Date)"),
      fieldtype: "Date",
      default: moment().startOf("year"),
    },
    {
      fieldname: "till_date",
      label: __("Till Date (Lead Creation Date)"),
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
  ],
};
