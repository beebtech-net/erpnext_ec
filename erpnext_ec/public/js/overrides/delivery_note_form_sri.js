var doctype_customized = "Delivery Note";

frappe.ui.form.on(doctype_customized, {
	refresh(frm)
    {
        if (frm.doc.status == 'Cancelled' || frm.doc.status == 'Draft') {
            return false;
        }
        
        SetFormSriButtons(frm, doctype_customized);
    },
})
