frappe.ui.form.on('Sales Invoice', {
	refresh(frm)
    {
        console.log(frm.doc);

        frm.add_custom_button(__('<i class="fa fa-play"></i> Enviar al SRI'), function() {
            // When this button is clicked, do this            
            
            console.log(frm.doc);
            
            console.log("Cargado Script add_custom_button ----cambiado");

            var subject = frm.doc.subject;
            var event_type = frm.doc.event_type;    

            PrepareDocumentForSend(frm.doc);

            // do something with these values, like an ajax request 
            // or call a server side frappe function using frappe.call
            //$.ajax({
            //    url: "http://example.com/just-do-it",
            //    data: {
            //        "subject": subject,
            //        "event_type": event_type
            //    }    
                // read more about $.ajax syntax at http://api.jquery.com/jquery.ajax/    
            //});

            /*
            //freeze_message accepts html WOOWW! <div></div>
            frappe.call({
                method: "erpnext_ec.utilities.sri_ws.send_doc",
                args: {
                    doc: frm.doc,
                    freeze: true,
                    freeze_message: "Procesando documento, espere un momento.",
                    success: function(r) {},
                    error: function(r) {},
                    always: function(r) {},
                },
                callback: function(r) 
                {
                    
                    if(r.message)
                    {
                        let root_company = r.message.length ? r.message[0] : "";
                        me.page.fields_dict.root_company.set_value(root_company);

                        frappe.db.get_value("Company", {"name": company}, "allow_account_creation_against_child_company", (r) => {
                            frappe.flags.ignore_root_company_validation = r.allow_account_creation_against_child_company;
                        });
                    }
                    
                }
            });*/

        },);

        frm.add_custom_button(__('<i class="fa fa-play"></i> Descargar XML'), function() 
        {

            //frappe.show_alert({
            //    message: __(`${frm.doc.name} aún se está configurando, espere un momento por favor.`),
            //    indicator: 'red'
            //}, 3);

            frappe.show_alert({
                message: __(`${frm.doc.name} Implementación requerida.`),
                indicator: 'red'
            }, 3);

        },__('<svg class="icon  icon-sm" style=""><use class="" href="#icon-organization"></use></svg>Sri')); //NO SOPORTA AWESOME ICONS
    },
})
