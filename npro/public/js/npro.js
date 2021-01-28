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

  set_chart_values: function (values) {
    values.y_fields = [];
    values.colors = [];
    if (values.y_axis_fields) {
      values.y_axis_fields.map((f) => {
        values.y_fields.push(f.y_field);
        values.colors.push(f.color);
      });
    }

    values.y_fields = values.y_fields.map((d) => d.trim()).filter(Boolean);

    return values;
  },

  create_chart: function (x_field, y_field, report) {
    let values = {
      x_field: x_field,
      chart_type: "Bar",
      y_axis_fields: [
        { color: "#ff8989", idx: 1, _islocal: true, y_field: y_field },
      ],
    };

    values = npro.utils.set_chart_values(values);
    let options = frappe.report_utils.make_chart_options(
      report.columns,
      report.raw_data,
      values
    );
    report.chart_fields = values;

    let x_field_label = frappe.model.unscrub(x_field);
    let y_field_label = frappe.model.unscrub(y_field);

    options.title = __("{0}: {1} vs {2}", [
      report.report_name,
      x_field_label,
      y_field_label,
    ]);

    report.render_chart(options);
    report.add_chart_buttons_to_toolbar(true);
  },
});
