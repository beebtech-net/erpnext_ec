var doctype_customized = "Delivery Note";

frappe.ui.form.on(doctype_customized, {
	refresh(frm)
    {
        if (cur_frm.doc.docstatus == 1 && frappe.model.can_create("Delivery Trip")) 
        {
			frm.add_custom_button(
				'<i class="fa fa-truck"></i> ' +  __('Delivery Trip'),
				function () {
					
					frappe.model.open_mapped_doc({
		                method: "erpnext.stock.doctype.delivery_note.delivery_note.make_delivery_trip",
		                frm: cur_frm,
		            });
					
				},
				__("Create")
			);
		}

        if (frm.doc.status == 'Cancelled' || frm.doc.status == 'Draft') {
            return false;
        }
        
        SetFormSriButtons(frm, doctype_customized);
    },
})
