var doctype_customized = "Purchase Receipt";

frappe.listview_settings[doctype_customized] = frappe.listview_settings[doctype_customized] || {};

frappe.listview_settings[doctype_customized] = {
    add_fields: ['numeroautorizacion', 'sri_estado', 'status'],
button: {
    show(doc) {        
        return doc.status !== 'Cancelled' && doc.status !== 'Draft';
    },
    get_label(doc) 
    {
        //console.log('get_label called for doc:', doc);
        const d = doc;
        if (!d) return frappe.utils.icon('play', 'sm');
        const autorizado = d.numeroautorizacion && d.numeroautorizacion !== '0' && d.sri_estado == 200;
        return autorizado
            ? frappe.utils.icon('send', 'sm')
            : frappe.utils.icon('play', 'sm');
    },
    get_description(doc) 
    {
        const d = doc;
        if (!d) return frappe.utils.icon('play', 'sm');
        const autorizado = d.numeroautorizacion && d.numeroautorizacion !== '0' && d.sri_estado == 200;

        return autorizado
            ? 'Enviar email'
            : 'Enviar al SRI';
    },
    action(doc) 
    {
        var actionButton = $('.list-actions > .btn-action[data-name="' + doc.name + '"]');

        if ($(actionButton).attr('endRender') != 'true') {
            frappe.show_alert({
                message: __(`${doc.name} aún se está configurando, espere un momento por favor.`),
                indicator: 'red'
            }, 3);
        }        
    }
},
dropdown_button: {
        get_label: __('⬇'),
        buttons: [
            {
                get_label: frappe.utils.icon('code', 'sm') + __(' Descargar XML'),
                show: function(doc) { return true; },
                action: function(doc) {
                    document.Website.DownloadXml_v2(doc.name);
                }
            },
            {
                get_label: __('📄 Descargar PDF'),
                show: function(doc) { return true; },
                action: function(doc) {
                    document.Website.DownloadPdf_v2(doc.name);
                }
            },
            {
                get_label: __('ⓘ Ver información'),
                show: function(doc) { return true; },
                action: function(doc) {
                    document.Website.ShowInfo(doc.name);
                }
            },
            {
                get_label: __('✍ XML Signed'),
                show: function(doc) { return true; }, // Puedes añadir condiciones aquí para controlar la visualización
                action: function(doc) {
                    document.Website.DownloadXmlSigned(doc.name);
                }
            }
        ]
    }
}