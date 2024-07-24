var doctype_customized = "Purchase Receipt";

frappe.listview_settings[doctype_customized] = frappe.listview_settings[doctype_customized] || {};

frappe.listview_settings[doctype_customized].button = {
    show(doc) {

        if (doc.status == 'Cancelled' || doc.status == 'Draft') {
            return false;
        }

        SetupCustomButtons(doc, doctype_customized);
        return true;
    },
    get_label() 
    {
        return __('<i class="fa fa-play"></i>');
    },
    get_description(doc) 
    {
        return __('Enviar al SRI')
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
}
