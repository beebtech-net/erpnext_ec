function AccountSriBuild(listview) {
    console.log("AccountSriBuild");
    //frappe.msgprint("ButtonFunction");
    var document_preview = `
           <p>Confirmar para crear los datos de las cuentas para el SRI?</p>
           <table>
               <tr>
                   <td><i class="fa fa-file"></i> Se eliminarán los formatos de impresión ya creados previamente</td>                   
               </tr>
               <tr>
                   <td><i class="fa fa-file"></i> Estos formatos son requeridos para el envío de RIDE</td>                   
               </tr>`;
    
    
    frappe.warn('Crear datos de cuentas para el SRI?',
                   document_preview,
                   () => {
                       frappe.call({
                           method: "erpnext_ec.utilities.settings_tools.load_accounts",
                           args: 
                           {
                               freeze: true,
                               freeze_message: "Procesando datos, espere un momento.",
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
                   'Confirmar creación de datos para el SRI'
               );    
}

frappe.listview_settings['Account'] = {
   refresh: function(listview) {
       listview.page.add_inner_button('<i class="fa fa-file"></i> Crear datos SRI', function() {
        AccountSriBuild(listview);
       });;
   },
};
