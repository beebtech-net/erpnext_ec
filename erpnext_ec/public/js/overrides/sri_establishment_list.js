
async function SriEstablishmentBuild (listview) {

    let d = new frappe.ui.Dialog({
        title: 'Crear datos de SRI?',
        fields: [
            {
                label: 'Company',
                fieldname: 'target_company',
                fieldtype: 'Link',
                reqd: 0,
                default: frappe.boot.sysdefaults.company,
                options: 'Company'
            },            
            //{
            //    label: 'Envío inmediato',
            //    fieldname: 'no_delayed',
            //    fieldtype: 'Check'
            //},  
            {
                label: '<i class="fa fa-file"></i> Se eliminarán los ya creados previamente </br>' +
                '<i class="fa fa-file"></i> Estos datos son requeridos para el envío de RIDE',
                fieldname: 'info',
                fieldtype: 'Heading',                    
            }
        ],            
        primary_action_label: 'Confirmar creación de datos del SRI',
        primary_action(values) {
            console.log(values.target_company);
            
            frappe.call({
                method: "erpnext_ec.utilities.settings_tools.load_sri_estab_build",
                args: 
                {
                     company: values.target_company,
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

            d.hide();
        }
    });
    
    html_current = $(d.modal_body[0]).find('.frappe-control[data-fieldname="info"]').css('font-size', '1em').css('margin-bottom', '10px').html();
    html_current = html_current.replace('<h4>','<h5>');
    html_current = html_current.replace('</h4>','</h5>');
    $(d.modal_body[0]).find('.frappe-control[data-fieldname="info"]').html(html_current);

    d.show();
}

frappe.listview_settings['Sri Establishment'] = {
   refresh: function(listview) {
       listview.page.add_inner_button('<i class="fa fa-file"></i> Crear datos', function() {
           SriEstablishmentBuild(listview);
       });;
   },
};
