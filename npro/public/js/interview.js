frappe.ui.form.on("Interview", {
    refresh: function (frm) {
        setTimeout(() => {
            frm.page.remove_inner_button("Submit Feedback")
        }, 1);
    },
});
