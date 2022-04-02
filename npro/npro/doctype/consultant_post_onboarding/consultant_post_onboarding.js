// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Consultant Post Onboarding', {
	setup: function (frm) {
		frm.add_fetch("consultant_post_onboarding_template", "company", "company");
		frm.add_fetch("consultant_post_onboarding_template", "department", "department");
		frm.add_fetch("consultant_post_onboarding_template", "designation", "designation");
	},

	refresh: function (frm) {
		if (frm.doc.employee) {
			frm.add_custom_button(__('Employee'), function () {
				frappe.set_route("Form", "Employee", frm.doc.employee);
			}, __("View"));
		}
		if (frm.doc.project) {
			frm.add_custom_button(__('Project'), function () {
				frappe.set_route("Form", "Project", frm.doc.project);
			}, __("View"));
			frm.add_custom_button(__('Task'), function () {
				frappe.set_route('List', 'Task', { project: frm.doc.project });
			}, __("View"));
		}
	},


	consultant_post_onboarding_template: function (frm) {
		frm.set_value("activities", "");
		if (frm.doc.consultant_post_onboarding_template) {
			frappe.call({
				method: "erpnext.hr.utils.get_onboarding_details",
				args: {
					"parent": frm.doc.consultant_post_onboarding_template,
					"parenttype": "Consultant Post Onboarding Template"
				},
				callback: function (r) {
					console.log(r.message);
					if (r.message) {
						$.each(r.message, function (i, d) {
							var row = frappe.model.add_child(frm.doc, "Employee Boarding Activity", "activities");
							$.extend(row, d);
						});
					}
					refresh_field("activities");
				}
			});
		}
	}
});
