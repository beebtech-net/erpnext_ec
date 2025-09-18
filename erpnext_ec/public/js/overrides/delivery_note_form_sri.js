var doctype_customized = "Delivery Note";

frappe.ui.form.on(doctype_customized, {
	refresh(frm)
    {
        frm.add_custom_button('<i class="fa fa-truck"></i> ' +  __('Delivery Trip'), function() {
            frappe.new_doc('Delivery Trip', {
                delivery_stops: [{
                    delivery_note: frm.doc.name
                }]
            });
        }, __('Create'));

        if (frm.doc.status == 'Cancelled' || frm.doc.status == 'Draft') {
            return false;
        }
        
        SetFormSriButtons(frm, doctype_customized);
    },
})
