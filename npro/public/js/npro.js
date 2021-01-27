frappe.provide("npro.utils");

Object.assign(npro.utils, {
  TIMESPAN_OPTIONS: [
    "Last Week",
    "Last Month",
    "Last Quarter",
    "Last Year",
    "Today",
    "This Week",
    "This Month",
    "This Quarter",
    "This Year",
  ],
  get_date_range: function (timespan = "This Month") {
    timespan = timespan.toLowerCase();
    let current_date = frappe.datetime.now_date();
    let date_range_map = {
      "this week": [frappe.datetime.week_start(), current_date],
      "this month": [frappe.datetime.month_start(), current_date],
      "this quarter": [frappe.datetime.quarter_start(), current_date],
      "this year": [frappe.datetime.year_start(), current_date],
      "last week": [frappe.datetime.add_days(current_date, -7), current_date],
      "last month": [
        frappe.datetime.add_months(current_date, -1),
        current_date,
      ],
      "last quarter": [
        frappe.datetime.add_months(current_date, -3),
        current_date,
      ],
      "last year": [
        frappe.datetime.add_months(current_date, -12),
        current_date,
      ],
      "all time": null,
      "select date range": this.selected_date_range || [
        frappe.datetime.month_start(),
        current_date,
      ],
    };
    return date_range_map[timespan];
  },
});
