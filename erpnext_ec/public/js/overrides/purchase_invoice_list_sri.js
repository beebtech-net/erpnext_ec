function UploadFromSriBuild(listview) 
{
    console.log("UploadFromSriBuild");
    //frappe.msgprint("ButtonFunction");

    let fu = new frappe.ui.FileUploader({
        //Metodo no es necesario, pero puede usarse para otros casos
        //method: 'erpnext_ec.utilities.import_tools.custom_upload',
        make_attachments_public: "False",
        dialog_title: "Importar XML del SRI",
        disable_file_browser: "False",
        dialog_primary_action_label:"Iniciar importación",
        //frm: frm,
        restrictions: {
            allowed_file_types: [".xml", ".zip"]
        },
        on_success (file)
        {
            console.log(file);
            console.log(cur_list);

            //if (cur_list.data.length > 0) {
                // don't replace existing capture
            //    return;
            //}
          
            var import_auto_create_data = document.getElementById('import_auto_create_data').checked;
            var import_update_invoices = document.getElementById('import_update_invoices').checked;
            var import_remove_files = document.getElementById('import_remove_files').checked;

            console.log(import_auto_create_data);
            console.log(import_update_invoices);
            console.log(import_remove_files);

            frappe.call({
                    method: "erpnext_ec.utilities.import_tools.import_purchase_invoice_from_xml",
                    args: 
                    {
                        file: file,
                        auto_create_data: import_auto_create_data,
                        update_invoices: import_update_invoices,
                        remove_files: import_remove_files,
                        freeze: true,
                        freeze_message: "Importando documentos, espere un momento.",
                        success: function(r) {},
                        always: function(r) {},
                    },
                    callback: function(r)
                    {
                        console.log(r);
                        
                        //jsonResponse = JSON.parse(r.message);
                        //console.log(jsonResponse);
                    },
                    error: function(r) {
                        
                    },
                });

            frappe.show_alert({
                message:__('File uploaded.'),
                indicator:'green'
            }, 5);


            //fu.dialog.show();
        }
    });

    console.log(fu);
    
    //Se agregan controles custom
    $(fu.dialog.body).append(`
    <div class="m-2">
        <div class="checkbox">
            <label>
                <span class="input-area"><input id="import_auto_create_data" type="checkbox" autocomplete="off" class="input-with-feedback" data-fieldtype="Check" data-fieldname="auto_create_data" placeholder="" checked></span>
                <span class="label-area">Crear datos no existentes (artículos, marcas, etc.)</span>        
            </label>    
        </div>
        <div class="checkbox">
            <label>
                <span class="input-area"><input id="import_update_invoices" type="checkbox" autocomplete="off" class="input-with-feedback" data-fieldtype="Check" data-fieldname="update_invoices" placeholder="" checked></span>
                <span class="label-area">Actualizar facturas existentes</span>        
            </label>    
        </div>
        <div class="checkbox">
            <label>
                <span class="input-area"><input id="import_remove_files" type="checkbox" autocomplete="off" class="input-with-feedback" data-fieldtype="Check" data-fieldname="remove_files" placeholder="" checked></span>
                <span class="label-area">Eliminar archivos al finalizar</span>        
            </label>    
        </div>
    </div>`);

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
                title: 'Importar de XML',
                fields: [
                    {
                        label: 'Arrastre el archivo zip que contiene los archivos XML que desea importar.',
                        fieldname: 'info',
                        fieldtype: 'Heading',                    
                    },
                    {
                        label: 'Adjuntos',
                        fieldname: 'attach_content',
                        fieldtype: 'Attach',
                        max_attachments: 20,
                        allow_multiple: true,
                        //allowed_file_types:"*.xlsx *.zip *.xml",
                        restrictions:
                        {
                            allowed_file_types:"xlsx"
                        }
                    },
                    {
                        label: 'Crear datos no existentes (artículos, marcas, etc.)',
                        fieldname: 'auto_create_data',
                        fieldtype: 'Check',
                        default: true
                    },
                    {
                        label: 'Actualizar facturas existentes',
                        fieldname: 'update_invoices',
                        fieldtype: 'Check',
                        default: true
                    },
                    {
                        label: 'Eliminar archivos al terminar',
                        fieldname: 'remove_files',
                        fieldtype: 'Check',
                        default: true
                    }
                ],            
                primary_action_label: 'Importar',
                primary_action(values) {
                    console.log(values);
                    
                    d.hide();

                    frappe.call({
                        method: "erpnext_ec.utilities.import_tools.import_purchase_invoice_from_xml",
                        args: 
                        {
                            attach_content: values.attach_content,
                            auto_create_data: values.auto_create_data,
                            freeze: true,
                            freeze_message: "Importando documentos, espere un momento.",
                            success: function(r) {},
                            always: function(r) {},
                        },
                        callback: function(r) 
                        {
                            console.log(r);
                            
                            //jsonResponse = JSON.parse(r.message);
                            //console.log(jsonResponse);
                        },
                        error: function(r) {
                            
                        },
                    });
                }
            });            
    
            //d.show();
    
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