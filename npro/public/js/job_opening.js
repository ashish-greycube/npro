frappe.ui.form.on('Job Opening', {
    refresh: function (frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Create Interview Round"), () => {
                let round = frappe.model.make_new_doc_and_get_name('Interview Round');
                round = locals['Interview Round'][round];
                round.round_name = `${frm.doc.job_title}-${frm.doc.customer_cf}`;
                round.designation = frm.doc.designation;
                (frm.doc.jrss_ct_cf || []).forEach(t => {
                    let skill = frappe.model.add_child(round, 'Expected Skill Set', 'expected_skill_set');
                    skill.skill = t.skill;
                    skill.description = t.description
                });
                frappe.set_route('Form', 'Interview Round', round.name);
            })

        }
    },

    customer_cf: function (frm) {
        frm.set_query('customer_contact_cf', function (doc) {
            return {
                query: "npro.api.get_contacts_for_customer",
                filters: { customer: frm.doc.customer_cf },
            };
        });
    },

    designation: function (frm) {
        if (frm.doc.designation) {
            frappe.model.with_doc("Designation", frm.doc.designation, () => {
                let designation = frappe.model.get_doc("Designation", frm.doc.designation);
                let skills = (frm.doc.jrss_ct_cf || []).map(t => t.skill);
                designation.skills.forEach((d) => {
                    if (!skills.includes(d.skill)) {

                        let row = frappe.model.add_child(frm.doc, 'JRSS CT', 'jrss_ct_cf');
                        row.skill = d.skill;
                        row.description = d.skill;
                    }
                });
                frm.refresh_field('jrss_ct_cf');
            });

        }

    },
});