frappe.ui.form.on("Opportunity", {
  status: function (frm) {
    if (frm.doc.status == "Lost" && frm.doc.lost_reasons.length == 0) {
      frm.trigger("set_as_lost_dialog");
    }
  },
  setup: function (frm) {
    frm.set_query("sales_stage", () => {
      return {
        filters: {
          opportunity_type_cf: ["in", [frm.doc.opportunity_type, ""]],
        },
      };
    });

    frm.set_query("previous_jo_cf", () => {
      return {
        filters: {
          opportunity_cf: frm.doc.previous_opportunity_cf || "?",
        },
      };
    });
  },
  refresh: function (frm) {
    frm.set_value("opportunity_from", "Customer", true);
  },

  opportunity_consulting_detail_ct_cf_on_form_rendered: function (
    doc,
    grid_row
  ) {
    grid_row = cur_frm.open_grid_row();
    let stage = grid_row.grid_form.fields_dict.stage.value;
    grid_row.toggle_display(
      "create_job_opening",
      stage === "NPro Candidate Sourcing"
    );
    if (stage === "NPro Candidate Sourcing") {
      let btn = grid_row.grid_form.fields_dict.create_job_opening;
      if (btn && btn.$input) {
        btn.$input.addClass("btn-primary");
      }
    }
  },

  previous_jo_cf: function (frm) {
    // Based on Previous Opp : Customer, Opportunity type, Business module, opportunity owner, Contact info.
    frappe.db
      .get_value(
        "Job Opening",
        frm.doc.previous_jo_cf,
        previous_job_opening_fetch_fields
      )
      .then((r) => {
        let details = frm.doc.opportunity_consulting_detail_ct_cf,
          is_added = false;
        if (details && details.length) {
          for (const d of details) {
            if (r.message.opportunity_technology_cf == d.project_name) {
              is_added = true;
              break;
            }
          }
        }

        if (!is_added) {
          let args = {
            project_name: r.message.opportunity_technology_cf,
            duration_in_months: r.message.contract_duration_cf,
            billing_per_month: r.message.billing_per_month_cf,
            location: r.message.location_cf,
            amount:
              flt(r.message.contract_duration_cf) *
              flt(r.message.billing_per_month_cf),
          };
          frm.add_child("opportunity_consulting_detail_ct_cf", args);
          frm.refresh_field("opportunity_consulting_detail_ct_cf");
        }
      });
  },

  previous_opportunity_cf: function (frm) {
    // Based on Previous JO : add a row in child table : Technology, duration, billing per month, location.
    frappe.db
      .get_value(
        "Opportunity",
        frm.doc.previous_opportunity_cf,
        previous_opportunity_fetch_fields
      )
      .then((r) => {
        for (const fld in r.message) {
          frm.set_value(fld, r.message[fld]);
        }
      });
  },
});

frappe.ui.form.on("Opportunity Consulting Detail CT", {
  stage: function (frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    let btn =
      frm.fields_dict[
        "opportunity_consulting_detail_ct_cf"
      ].grid.grid_rows_by_docname[cdn].get_field("create_job_opening");
    if (item.stage == "NPro Candidate Sourcing") {
      btn.toggle(true);
    } else {
      btn.toggle(false);
    }
  },

  create_job_opening: function (frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    let opening = frappe.model.make_new_doc_and_get_name("Job Opening");
    opening = locals["Job Opening"][opening];
    $.extend(opening, {
      company: frm.doc.company,
      opportunity_cf: frm.doc.name,
      opportunity_consulting_detail_ct_cf: cdn,
      opportunity_technology_cf: item["project_name"],
      job_title: item["project_name"],
      customer_cf: frm.doc.party_name,
      customer_contact_cf: frm.doc.contact_person,
      customer_email_cf: frm.doc.contact_email,
      // npro_sourcing_owner_cf: frm.doc.opportunity_owner_cf, // removed on 31-01-2022
      contract_duration_cf: item.duration_in_months,
      billing_per_month_cf: item.billing_per_month,
      location_cf: item.location,
    });

    frappe.set_route("Form", "Job Opening", opening.name);
  },
});

const previous_opportunity_fetch_fields = [
  "opportunity_owner_cf",
  "opportunity_type",
  "opportunity_from",
  "party_name",
  "business_module",
  "customer_address",
  "address_display",
  "territory",
  "customer_group",
  "contact_person",
  "contact_display",
  "contact_email",
  "contact_mobile",
];

const previous_job_opening_fetch_fields = [
  // Technology, duration, billing per month, location.
  "contract_duration_cf",
  "billing_per_month_cf",
  "opportunity_technology_cf",
  "location_cf",
];
