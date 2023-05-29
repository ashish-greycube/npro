frappe.provide("npro.utils");

$(document).on("form-refresh", function (e, frm) {
  console.log(frm);
  window.frm = frm;
  window.doc = frm.doc;
});

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
    if (timespan == "today") {
      return [current_date, current_date];
    } else if (timespan.startsWith("this ")) {
      timespan = timespan.replace("this ", "");
      return [
        moment().startOf(timespan).format(),
        moment().endOf(timespan).format(),
      ];
    } else if (timespan.startsWith("last ")) {
      timespan = timespan.replace("last ", "");
      return [
        moment().subtract(1, timespan).startOf(timespan).format(),
        moment().subtract(1, timespan).endOf(timespan).format(),
      ];
    } else if (timespan == "all time") {
      return ["2000-01-01", current_date];
    } else {
      return [moment().startOf("month").format(), current_date];
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
  check_numeric: function (fieldname, frm, raise) {
    if (frm.doc[fieldname] && isNaN(frm.doc[fieldname])) {
      let args = {
        title: __("Invalid {0}.", [frm.fields_dict[fieldname].df.label.bold()]),
        message: __("Please enter a numeric value.."),
      };
      if (raise) {
        frappe.throw(args);
      } else return args;
    }
  },

  validate_email: function (fieldname, frm, raise) {
    if (!frappe.utils.validate_type(frm.doc[fieldname], "email")) {
      let args = {
        message: __("Invalid email for {0}.", [
          frm.fields_dict[fieldname].df.label.bold(),
        ]),
      };
      if (raise) {
        frappe.throw(args);
      } else return args;
    }
  },

  check_validate: function (arr) {
    let messages = [];
    for (const fn of arr) {
      messages.push(fn[0](fn[1], fn[2]));
    }
    messages = messages
      .filter((t) => t)
      .map((t) => {
        return `${t.title} ${t.message}`;
      });

    if (messages.length) {
      frappe.throw({
        title: __("Validation error."),
        message: messages.join("<br>"),
      });
    }
  },

  guess_style: function (text, default_style, _colour) {
    // Override frappe utils function
    // to fix list indicator for Job Applicant
    var style = default_style || "default";
    var colour = "gray";
    if (text) {
      if (has_words(["Pending", "Review", "Medium", "Not Approved"], text)) {
        style = "warning";
        colour = "orange";
      } else if (
        has_words(
          ["Open", "Urgent", "High", "Failed", "Rejected", "Error"],
          text
        )
      ) {
        style = "danger";
        colour = "red";
      } else if (
        has_words(
          [
            "Closed",
            "Finished",
            "Converted",
            "Completed",
            "Complete",
            "Confirmed",
            "Approved",
            "Yes",
            "Active",
            "Available",
            "Paid",
            "Success",
            "Accepted",
          ],
          text
        )
      ) {
        style = "success";
        colour = "green";
      } else if (has_words(["Submitted"], text)) {
        style = "info";
        colour = "blue";
      } else if (text.match(/reject/gi)) {
        style = "danger";
        colour = "red";
      }
    }
    return _colour ? colour : style;
  },
});

$(document).ready(function () {
  if (frappe.boot.is_user_consent !== 1) {
    setInterval(() => {
      get_user_consent();
    }, 5000);
  }
});

const get_user_consent = function () {
  let doctype = "NPro User Consent";

  if (cur_dialog && cur_dialog.doc.doctype === doctype) {
    return;
  }

  function _after_insert() {
    let dlg = frappe.msgprint({
      message: __("Thank you for your consent. You will need to login again."),
      title: __("Thank you for your consent."),
    });
    dlg.keep_open = true;
    dlg.custom_onhide = function () {
      frappe.app.logout();
    };
  }

  frappe.model.with_doctype(doctype, () => {
    frappe.db
      .get_single_value("NPro Settings", "npro_user_consent")
      .then((consent) => {
        let new_doc = frappe.model.get_new_doc(doctype);
        new_doc.user = frappe.session.user;
        new_doc.consent = consent;
        frappe.ui.form.make_quick_entry(
          doctype,
          _after_insert,
          null,
          new_doc,
          true
        );
      });
  });
};
