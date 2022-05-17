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
    if (timespan == 'today') {
      return [current_date, current_date]
    } else if (timespan.startsWith('this ')) {
      timespan = timespan.replace('this ', '')
      return [
        moment().startOf(timespan).format(), moment().endOf(timespan).format(),
      ]
    } else if (timespan.startsWith('last ')) {
      timespan = timespan.replace('last ', '')
      return [
        moment().subtract(1, timespan).startOf(timespan).format(),
        moment().subtract(1, timespan).endOf(timespan).format(),
      ]
    } else if (timespan == 'all time') {
      return [
        '2000-01-01',
        current_date
      ]
    } else {
      return [
        moment().startOf('month').format(), current_date
      ]
    }

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

  create_chart: function (x_field, columns, datatable, report) {
    if (!report.data || !report.data.length) return;

    function get_y_axis_fields(datatable) {
      let y_axis_fields = [];
      let data = datatable.datamanager.data;
      for (const key in columns) {
        if (Object.hasOwnProperty.call(columns, key)) {
          if (data.some((x) => x[key] > 0)) {
            y_axis_fields.push({
              color: columns[key],
              y_field: key,
            });
          }
        }
      }
      return y_axis_fields;
    }
    let y_axis_fields = get_y_axis_fields(datatable);
    let chart = {
      chart_type: "Bar",
      x_field: x_field,
      y_axis_fields: y_axis_fields,
    };

    let values = npro.utils.set_chart_values(chart);
    let options = frappe.report_utils.make_chart_options(
      report.columns,
      report.raw_data,
      values
    );
    report.chart_fields = values;

    let x_field_label = frappe.model.unscrub(chart.x_field);
    let y_field_label = frappe.model.unscrub(chart.y_field);

    options.title = __("{0}", [
      report.report_name,
      x_field_label,
      y_field_label,
    ]);

    report.render_chart(options);
    // report.add_chart_buttons_to_toolbar(true);
  },
});

frappe.provide("frappe.utils");

Object.assign(frappe.utils, {
  guess_style: function (text, default_style, _colour) {
    // Override frappe utils function
    // to fix list indicator for Job Applicant
    var style = default_style || "default";
    var colour = "gray";
    if (text) {
      if (has_words(["Pending", "Review", "Medium", "Not Approved"], text)) {
        style = "warning";
        colour = "orange";
      } else if (has_words(["Open", "Urgent", "High", "Failed", "Rejected", "Error"], text)) {
        style = "danger";
        colour = "red";
      } else if (has_words(["Closed", "Finished", "Converted", "Completed", "Complete", "Confirmed",
        "Approved", "Yes", "Active", "Available", "Paid", "Success"], text)) {
        style = "success";
        colour = "green";
      } else if (has_words(["Submitted"], text)) {
        style = "info";
        colour = "blue";
      } else if (text.match(/reject/ig)) {
        style = "danger";
        colour = "red";
      }
    }
    return _colour ? colour : style;
  }
})

