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
    onload: function (listview) {
		var buttonObj = listview.page.add_inner_button('<i class="fa fa-file"></i> Crear datos SRI', function() {
            AccountSriBuild(listview);
           });
        
        //TODO: Para que no se oculte en pantalla pequeña se va a requerir 
        // crear un metodo que construya un nuevo div
        // con estilos propios, ya que el div donde se agregan los botones 
        // tiene por defecto un estilo par ocultarse en pantallas pequeñas

        //console.log(buttonObj);
        //$(buttonObj).parent().removeClass('hidden-xs');
        //$(buttonObj).parent().removeClass('hidden-md');
	},
   //refresh: function(listview) {
   //    listview.page.add_inner_button('<i class="fa fa-file"></i> Crear datos SRI', function() {
   //     AccountSriBuild(listview);
   //    });
   //},
};
