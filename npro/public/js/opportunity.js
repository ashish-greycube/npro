frappe.ui.form.on("Opportunity", {
    status: function (frm) {
        if (frm.doc.status == 'Lost' && frm.doc.lost_reasons.length == 0) {
            frm.trigger('set_as_lost_dialog');
        }
    },
    setup: function (frm) {
        frm.set_query('sales_stage', () => {
            return {
                filters: {
                    opportunity_type_cf: ['in', [frm.doc.opportunity_type, ""]]
                }
            }
        })
    },
    refresh: function (frm) {
        frm.set_value('opportunity_from', 'Customer', true)

    }
})

frappe.ui.form.on("Opportunity Consulting Detail CT", {
    stage: function (frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        let btn = frm.fields_dict["opportunity_consulting_detail_ct_cf"].grid.grid_rows_by_docname[cdn].get_field("create_job_opening")
        if (item.stage == "NPro Candidate Sourcing") {
            btn.toggle(true)
        } else {
            btn.toggle(false)
        }
    },

    create_job_opening: function (frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        let opening = frappe.model.make_new_doc_and_get_name("Job Opening");
        opening = locals['Job Opening'][opening];
        $.extend(opening, {
            company: frm.doc.company,
            opportunity_cf: frm.doc.name,
            customer_cf: frm.doc.party_name,
            customer_contact_cf: frm.doc.contact_person,
            customer_email_cf: frm.doc.contact_email,
            npro_sourcing_owner_cf: frm.doc.opportunity_owner_cf,
            contract_duration_cf: item.duration_in_months,
            billing_per_month_cf: item.billing_per_month,
            location_cf: item.location
        });

        frappe.set_route('Form', 'Job Opening', opening.name);

    }
})