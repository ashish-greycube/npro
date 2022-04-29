frappe.listview_settings['Consultant Post Onboarding'] = {
    add_fields: ["post_boarding_status",],
    // filters:[["boarding_status","=", "Pending"]],
    get_indicator: function (doc) {
        return [__(doc.post_boarding_status), frappe.utils.guess_colour(doc.post_boarding_status), "status,=," + doc.post_boarding_status];
    }
};
