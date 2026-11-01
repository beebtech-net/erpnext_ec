var doctype_customized = "Sales Invoice";

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

    // button: {
    //     show(doc) {            
    //         return doc.status !== 'Cancelled' && doc.status !== 'Draft';
    //     },
    //     get_label() {
            
    //         return frappe.utils.icon('setting', 'sm') + ' ' + __('Acciones');
    //     },
    //     get_description() {
    //         return __('Haga clic para ver más acciones');
    //     },
    //     action(doc) {
            
            
    //         const menuHtml = `
    //             <div class="custom-action-menu" style="position: absolute; z-index: 1050; background: white; border: 1px solid #d1d8dd; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); min-width: 180px;">
    //                 <a class="dropdown-item" href="#" data-action="xml" style="padding: 8px 12px; display: flex; align-items: center;">
    //                     <i class="fa fa-file-code-o" style="margin-right: 8px; width: 16px;"></i> ${__('Descargar XML')}
    //                 </a>
    //                 <a class="dropdown-item" href="#" data-action="pdf" style="padding: 8px 12px; display: flex; align-items: center;">
    //                     <i class="fa fa-file-pdf-o" style="margin-right: 8px; width: 16px;"></i> ${__('Descargar PDF')}
    //                 </a>
    //                 <div style="height: 1px; background: #d1d8dd; margin: 4px 0;"></div> <!-- Línea divisoria -->
    //                 <a class="dropdown-item" href="#" data-action="info" style="padding: 8px 12px; display: flex; align-items: center;">
    //                     <i class="fa fa-info-circle" style="margin-right: 8px; width: 16px;"></i> ${__('Ver información')}
    //                 </a>
    //                 <a class="dropdown-item" href="#" data-action="signed" style="padding: 8px 12px; display: flex; align-items: center;">
    //                     <i class="fa fa-pencil-square-o" style="margin-right: 8px; width: 16px;"></i> ${__('XML Firmado')}
    //                 </a>
    //             </div>
    //         `;
    //         const $menu = $(menuHtml).appendTo('body').css('position', 'fixed');
            
    //         const $triggerBtn = $(`.list-row .btn-action[data-name="${doc.name}"]`).first();

    // if ($triggerBtn.length) {
    //     const btnRect = $triggerBtn[0].getBoundingClientRect();
    //     const menuHeight = $menu.outerHeight();
    //     const spaceBelow = window.innerHeight - btnRect.bottom;
    //     const top = spaceBelow < menuHeight
    //         ? btnRect.top - menuHeight - 5
    //         : btnRect.bottom + 5;
    //     $menu.css({
    //         top: top + 'px',
    //         left: btnRect.left + 'px'
    //     });
    // } else {
        
    //     $menu.css({
    //         top: '50%',
    //         left: '50%',
    //         transform: 'translate(-50%, -50%)'
    //     });
    // }

            
    //         $menu.find('[data-action]').on('click', function(e) {
    //             e.preventDefault();
    //             const action = $(this).data('action');
    //             if (action === 'xml') document.Website.DownloadXml_v2(doc.name);
    //             if (action === 'pdf') document.Website.DownloadPdf_v2(doc.name);
    //             if (action === 'info') document.Website.ShowInfo(doc.name);
    //             if (action === 'signed') document.Website.DownloadXmlSigned(doc.name);
    //             $menu.remove(); 
    //         });
            
    //         setTimeout(() => {
    //             $(document).one('click', function() {
    //                 $menu.remove();
    //             });
    //         }, 0);
    //     }
    // },

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