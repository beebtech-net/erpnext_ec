frappe.ui.form.on('Sri Signature', {
    onload: function(frm) {                
        
    },
    refresh(frm)
    {
        frm.add_custom_button(__("Comprobar"), function() {
            //console.log("-----> PRO");

            frappe.call({
                method: "erpnext_ec.utilities.sri_ws.test_signaure",
                args: 
                {
                    signature_doc: frm.doc,                    
                    //freeze: true,
                    //freeze_message: "Procesando documento, espere un momento.",
                    success: function(r) {},								
                    always: function(r) {},
                },
                callback: function(r) 
                {
                    console.log(r);

                    //jsonResponse = JSON.parse(r.message);
                    //console.log(jsonResponse);
                    frappe.show_alert({
                        message: __(`Error al procesar firma:`),
                        indicator: 'red'
                    }, 10);                    

                },
                error: function(r) {
                    
                },
            });
        });
    },    
});
