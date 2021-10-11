// Copyright (c) 2016, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

const template = `
<div> {{contact}} </div>
<div> {{email_id}} </div>
<div> {{mobile_no}} </div>
`;

frappe.query_reports["Customer Organization Chart"] = {
  filters: [
    {
      fieldname: "customer",
      label: __("Customer"),
      fieldtype: "Link",
      options: "Customer",
      reqd: true,
    },
  ],

  onload: function (report) {
    frappe.require(["assets/npro/js/lib/loader.js"], () => {
      google.charts.load("current", { packages: ["orgchart"] });

      google.charts.setOnLoadCallback(() => {
        report.org_chart = new frappe.GoogleChart(report, {});
        setTimeout(() => {
          report.refresh();
        }, 500);
      });
    });
  },
};

frappe.GoogleChart = Class.extend({
  init: function (report, opts) {
    this.report = report;
    this.setup();
    this.make(report);
  },

  setup() {
    let me = this;
    this.toggle_frappe_datatable(true);

    // monkey-patch refresh as frappe query_report does not provide refresh event
    this.original_refresh = this.report.refresh;
    this.report.refresh = function () {
      me.original_refresh.apply(this, arguments).then(() => {
        me.set_data();
      });
    };
    // destroy tabulator when navigating away
    window.addEventListener("hashchange", this.destroy.bind(this), {
      once: true,
    });
  },

  make() {
    let me = this,
      el = $(
        "<div id='org-container' style='display:flex;overflow-x:auto' class='.org-container'></div>"
      );
    el.insertBefore($(".report-wrapper"));

    me.org_chart = new google.visualization.OrgChart(
      document.getElementById("org-container")
    );
  },

  destroy(e) {
    this.report.refresh = this.original_refresh;
    // this.tabulator && this.tabulator.destroy();
    $("#org-container").remove();
    this.toggle_frappe_datatable(false);
    // need to set route_options here to force refresh when navigating back to same report
    frappe.route_options = { _t: new Date().getTime() };
  },

  set_data() {
    if (this.org_chart) {
      var data = new google.visualization.DataTable();

      data.addColumn("string", "Name");
      data.addColumn("string", "Manager");
      data.addColumn("string", "ToolTip");

      this.report.data.forEach((el) => {
        // Add a row with two cells, the second with a formatted value.

        data.addRow([
          {
            v: el.contact,
            f: frappe.render(template, el),
          },
          el.reports_to_cf,
          `${el.email_id} ${el.mobile_no}`,
        ]);
      });

      this.org_chart.draw(data, { allowHtml: true });
    }
  },

  toggle_frappe_datatable(flag) {
    // hide frappe report datatable and message area
    // $(".datatable").toggleClass("hidden d-none", flag);
    // this.report.$message.toggleClass("hidden d-none", flag);
  },
});

// var dataSourceUrl = 'https://spreadsheets.google.com/tq?key=rCaVQNfFDMhOM6ENNYeYZ9Q&pub=1';

// <html>
//   <head>
//     <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
//     <script type="text/javascript">
//       google.charts.load('current', {packages:["orgchart"]});
//       google.charts.setOnLoadCallback(drawChart);

//       function drawChart() {
//         var data = new google.visualization.DataTable();
//         data.addColumn('string', 'Name');
//         data.addColumn('string', 'Manager');
//         data.addColumn('string', 'ToolTip');

//         // For each orgchart box, provide the name, manager, and tooltip to show.
//         data.addRows([
//           [{'v':'Mike', 'f':'Mike<div style="color:red; font-style:italic">President</div>'},
//            '', 'The President'],
//           [{'v':'Jim', 'f':'Jim<div style="color:red; font-style:italic">Vice President</div>'},
//            'Mike', 'VP'],
//           ['Alice', 'Mike', ''],
//           ['Bob', 'Jim', 'Bob Sponge'],
//           ['Carol', 'Bob', '']
//         ]);

//         // Create the chart.
//         var chart = new google.visualization.OrgChart(document.getElementById('chart_div'));
//         // Draw the chart, setting the allowHtml option to true for the tooltips.
//         chart.draw(data, {'allowHtml':true});
//       }
//    </script>
//     </head>
//   <body>
//     <div id="chart_div"></div>
//   </body>
// </html>
