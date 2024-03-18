async function SequenceSriBuild (listview) {
    console.log("SequenceSriBuild");
    //frappe.msgprint("ButtonFunction");

    var companyApi = await frappe.db.get_list('Company');

    var company_name = "";

    if(companyApi != null && companyApi != undefined && companyApi.length > 0)
    {
        company_name = companyApi[0].name;
    }

    if(company_name == "")
    {
        frappe.show_alert({                    
            message: __(`Error al procesar: No hay compañia seleccionada:`),
            indicator: 'red'
        }, 5);
        return;
    }

    var document_preview = `
           <p>Confirmar para crear los secuenciales para el SRI?</p>
           <table>
               <tr>
                   <td><i class="fa fa-file"></i> Se eliminarán los formatos de impresión ya creados previamente</td>                   
               </tr>
               <tr>
                   <td><i class="fa fa-file"></i> Estos secuenciales son requeridos para el envío de RIDE</td>                   
               </tr>
               <tr>
                   <td>Compañia destino: <strong>${company_name}</strong></td>
               </tr>`;    
    
    frappe.warn('Crear Secuenciales SRI?',
                   document_preview,
                   () => {
                       frappe.call({
                           method: "erpnext_ec.utilities.settings_tools.load_sri_sequences",
                           args: 
                           {
                                company: company_name,
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
                   'Confirmar creación de secuenciales SRI'
               );    
}

frappe.listview_settings['Sri Sequence'] = {
   refresh: function(listview) {
       listview.page.add_inner_button('<i class="fa fa-file"></i> Crear Secuenciales SRI', function() {
           SequenceSriBuild(listview);
       });;
   },
};