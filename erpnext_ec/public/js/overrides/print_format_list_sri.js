function PrintFormatSriBuild(listview) {
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

function PrintFormatSriBuildOnline(listview) {
    console.log("PrintFormatSriBuildOnline");
    //frappe.msgprint("ButtonFunction");
    var document_preview = `
           <p>Confirmar para crear los formatos de impresión para el SRI Online?</p>
           <table>
               <tr>
                   <td><i class="fa fa-file"></i> Se eliminarán los formatos de impresión ya creados previamente</td>                   
               </tr>
               <tr>
                   <td><i class="fa fa-file"></i> Estos formatos son requeridos para el envío de RIDE</td>                   
               </tr>`;    
    
    frappe.warn('Crear Formatos SRI Online?',
                   document_preview,
                   () => {
                       frappe.call({
                           method: "erpnext_ec.utilities.settings_tools.load_print_format_sri_online",
                           args: 
                           {
                               freeze: true,
                               freeze_message: "Procesando documento, espere un momento.",
                               success: function(r) {},								
                               always: function(r) {},
                           },
                           callback: function(r) 
                           {                               
                               frappe.show_alert({
                                    message: __(`Proceso realizado con éxito`),
                                    indicator: 'green'
                                }, 5);
                           },
                           error: function(r) {                               
                               frappe.show_alert({
                                message: __(`Error en proceso`),
                                indicator: 'red'
                                }, 10);
                           },
                       });
                   },
                   'Confirmar creación de formatos SRI Online'
               );    
}

frappe.listview_settings['Print Format'] = {
   refresh: function(listview) {
       listview.page.add_inner_button('<i class="fa fa-file"></i> Crear Formatos SRI', function() {
           PrintFormatSriBuild(listview);
       });

       listview.page.add_inner_button('<i class="fa fa-file"></i> Formatos SRI Online', function() {
            PrintFormatSriBuildOnline(listview);
        });
   },
};