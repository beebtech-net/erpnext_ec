
frappe.ui.form.on('Sri Type Doc', {
    onload: function(frm) {
        // Tu lógica personalizada aquí
        console.log("Sri Type Doc:" + Date().toString());

        
        
    },
    refresh(frm)
    {
        frm.add_custom_button(__("Do Something"), function() {
            // When this button is clicked, do this
    
            var subject = frm.doc.subject;
            var event_type = frm.doc.event_type;
    
            // do something with these values, like an ajax request 
            // or call a server side frappe function using frappe.call
            $.ajax({
                url: "http://example.com/just-do-it",
                data: {
                    "subject": subject,
                    "event_type": event_type
                }
    
                // read more about $.ajax syntax at http://api.jquery.com/jquery.ajax/
    
            });
        });
    },
    
    /*onload_post_render: function(frm){
        var bt = ['Delivery', 'Work Order', 'Invoice', 'Material Request', 'Request for Raw Materials', 'Purchase Order', 'Payment Request', 'Payment', 'Project', 'Subscription']
        bt.forEach(function(bt){
            frm.page.remove_inner_button(bt, 'Create')
        });
        frm.page.add_inner_button('Order Raw Materials', cur_frm.cscript.make_raw_material_request(), 'Create') 
    },
    */
    setup(frm) {
        // write setup code

        console.log("Setup:" + Date().toString());

        frm.add_custom_button('Open Reference form', () => {
            frappe.set_route('Form', frm.doc.reference_type, frm.doc.reference_name);
        })

        frm.custom_make_buttons = {
			'Work Order': 'Work Order / Subcontract PO',
			'Material Request': 'Material Request',
		};
    }
});
