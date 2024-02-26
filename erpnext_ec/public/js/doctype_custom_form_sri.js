
// doctypes_allowed_custom = [    
//     "Delivery Note",
//     "Purchase Invoice",    
//     "Sales Order",
//     "Sales Invoice"	
// ]

// setTimeout(
//     async function () {
//         doctype_customized = frappe.dynamic_link.doc.doctype;
//         console.log(doctype_customized);

//         //if( doctypes_allowed_custom )
//         //{
//             SetFormSriButtons(doctype_customized);
//         //}
//     },2000);

var doctype_customized = "[DOCTYPE_CUSTOM_FORM_SRI]";

frappe.ui.form.on(doctype_customized, {
	refresh(frm)
    {
        if (frm.doc.status == 'Cancelled' || frm.doc.status == 'Draft') {
            return false;
        }

        console.log(frm.doc);
        SetFormSriButtons(frm, doctype_customized);

        // frm.add_custom_button(__('<i class="fa fa-play"></i> Enviar al SRI'), function() {
        //     console.log(frm.doc);
            
        //     console.log("Cargado Script add_custom_button ----cambiado");

        //     var subject = frm.doc.subject;
        //     var event_type = frm.doc.event_type;
        //     PrepareDocumentForSend(frm.doc);
        // },);

        // frm.add_custom_button(__('<i class="fa fa-play"></i> Descargar XML'), function() 
        // {

        //     frappe.show_alert({
        //         message: __(`${frm.doc.name} Implementación requerida.`),
        //         indicator: 'red'
        //     }, 3);

        // },__('<svg class="icon  icon-sm" style=""><use class="" href="#icon-organization"></use></svg>Sri')); //NO SOPORTA AWESOME ICONS
    },
})
