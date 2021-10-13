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
    frappe.require(
      [
        "assets/npro/js/lib/loader.js",
        "assets/npro/js/lib/dom-to-image.min.js",
        "assets/npro/js/lib/download.min.js",
      ],
      () => {
        google.charts.load("current", { packages: ["orgchart"] });

        google.charts.setOnLoadCallback(() => {
          report.org_chart = new frappe.GoogleChart(report, {});
          setTimeout(() => {
            report.refresh();
          }, 500);
        });
      }
    );
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

    frappe.router.on("change", () => {
      me.destroy();
    });

    this.add_buttons();
  },

  // `<div id='org-container' style='display:flex;overflow-x:auto' class='.org-container'></div>`

  make() {
    let me = this,
      el = $(
        `<div id='org-container' style='display:flex;overflow-x:auto'></div> `
      );
    el.insertBefore($(".report-wrapper"));

    me.org_chart = new google.visualization.OrgChart(
      document.getElementById("org-container")
    );
  },

  destroy(e) {
    this.report.refresh = this.original_refresh;
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

      this.org_chart_data = data;
      this.org_chart.draw(data, { allowHtml: true });
    }
  },

  toggle_frappe_datatable(flag) {
    // hide frappe report datatable and message area
    // $(".datatable").toggleClass("hidden d-none", flag);
    // this.report.$message.toggleClass("hidden d-none", flag);
  },

  add_buttons() {
    var me = this;
    this.report.page.add_inner_button("Download Chart", () => {
      let customer = frappe.query_report.get_filter_value("customer");
      let el = $(`
      <div>
      <style>
      .no-show {
        position:absolute;
        left:-3000px;
      }
      .title {
        text-align:center;
        font-size: 1.5em;
        font-weight: bold;
      }
      </style>
      <div class='no-show'>
        <div id="print-div">
          <div class="title">
              ${customer} Organization Chart
          </div>
          <div id='org-print'>         
          </div>
        </div>
      </div>
      </div>
      `);
      el.insertAfter($(".layout-main"));

      var chart = new google.visualization.OrgChart(
        document.getElementById("org-print")
      );
      chart.draw(me.org_chart_data, { allowHtml: true });
      download_as_image("print-div", `${customer} - Organization Chart.png`);
      // var printContents = document.getElementById("org-container").innerHTML;
      // var printWindow = window.open(
      //   "",
      //   "",
      //   "height=400,width=600,top=100,left=300"
      // );
      // let html = `
      // <html>
      //   <head>
      //     <link rel="stylesheet" href="https://www.gstatic.com/charts/51/css/orgchart/orgchart.css"  type="text/css" />
      //   </head>
      //   <body onload="">${printContents}</body>
      // </html> `;
      // printWindow.document.write(html);
      // printWindow.document.close();
    });
  },
});

function download_as_image(element_id, filename) {
  var node = document.getElementById(element_id);

  domtoimage
    .toPng(node)
    .then(function (dataUrl) {
      download(dataUrl, filename, "image/png");
      node.remove();
    })
    .catch(function (error) {
      console.error("oops, something went wrong!", error);
    });
}
