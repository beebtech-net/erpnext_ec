function EmailTemplateSriBuild(listview) {
    console.log("EmailTemplateSriBuild");
    //frappe.msgprint("ButtonFunction");
    var document_preview = `
           <p>Confirmar para crear plantillas de email para el SRI?</p>
           <table>
               <tr>
                   <td><i class="fa fa-file"></i> Se eliminarán las plantillas ya creadas previamente</td>                   
               </tr>
               <tr>
                   <td><i class="fa fa-file"></i> Estas plantillas son requeridas para el envío de RIDE</td>                   
               </tr>`;
    
    
    frappe.warn('Crear Formatos SRI?',
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
                               frappe.show_alert({
                                    message: __(`Proceso realizado con éxito`),
                                    indicator: 'green'
                                }, 5);
                           },
                           error: function(r) {
                               //$(btnProcess).show();
                               //$(btnProcess).parent().find('.custom-animation').remove();
                               frappe.show_alert({
                                message: __(`Error en proceso`),
                                indicator: 'red'
                                }, 10);
                           },
                       });
                   },
                   'Confirmar creación de formatos SRI'
               );    
}

frappe.listview_settings['Email Template'] = {
   refresh: function(listview) {
       listview.page.add_inner_button('<i class="fa fa-file"></i> Crear Formatos SRI', function() {
           EmailTemplateSriBuild(listview);
       });;
   },
};