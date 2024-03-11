function UploadFromSriBuild(listview) 
{
    console.log("PrintFormatSriBuild");
    //frappe.msgprint("ButtonFunction");
    var document_preview = `
           <p>Confirmar para crear los formatos de impresion para el SRI?</p>
           <table>
               <tr>
                   <td><i class="fa fa-file"></i> Se eliminarán los formatos de impresión ya creados previamente</td>                   
               </tr>
               <tr>
                   <td><i class="fa fa-file"></i> Estos formatos son requeridos para el envío de RIDE</td>                   
               </tr>`;



               let d = new frappe.ui.Dialog({
                title: 'Enviar email',
                fields: [
                    {
                        label: 'Email',
                        fieldname: 'email_to',
                        fieldtype: 'Data',
                        reqd: 1,
                        default: 'ronald.chonillo@gmail.com'
                    },
                    {
                        label: 'Copia (cc)',
                        fieldname: 'email_cc',
                        fieldtype: 'Attach'
                    },
                    {
                        label: 'Envío inmediato',
                        fieldname: 'no_delayed',
                        fieldtype: 'Check'
                    },  
                    {
                        label: 'Este email se enviará con el XML y el PDF adjuntos',
                        fieldname: 'info',
                        fieldtype: 'Heading',                    
                    },
                ],            
                primary_action_label: 'Importar',
                primary_action(values) {
                    
    
                    d.hide();
                }
            });
            
    
            d.show();

            


    
    /*
    frappe.warn('Importar Facturas de Compra del SRI',
                   document_preview,
                   () => {
                       frappe.call({
                           method: "erpnext_ec.utilities.settings_tools.load_print_format_sri",
                           args: 
                           {
                               freeze: true,
                               freeze_message: "Procesando documento, espere un momento.",
                               success: function(r) {},								
                               always: function(r) {},
                           },
                           callback: function(r) 
                           {
                               //console.log(r);

                               //jsonResponse = JSON.parse(r.message);
                               //console.log(jsonResponse);
                           },
                           error: function(r) {
                               $(btnProcess).show();
                               $(btnProcess).parent().find('.custom-animation').remove();
                           },
                       });
                   },
                   'Iniciar importación del SRI'
               );   */ 
}

frappe.listview_settings['Purchase Invoice'] = {
   refresh: function(listview) {
       listview.page.add_inner_button('<i class="fa fa-upload"></i> Importar del SRI', function() {
        UploadFromSriBuild(listview);
       });;
   },
};