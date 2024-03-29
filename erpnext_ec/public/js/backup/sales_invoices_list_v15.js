


function SetupCustomButtons(doc)
{
    setTimeout(
        async function () {

            //console.log(doc);

            var buttonGroupExists = $('div.dropdown[data-name="' + doc.name + '"]');
            if (buttonGroupExists.length > 0) {
                //Evitamos que se renderice varias veces el botón de opciones
                return false;
            }
            
            //console.log(doc.name);
            var docApi = await frappe.db.get_doc('Sales Invoice', doc.name);
            //var docApi = frappe.get_doc('Sales Invoice', doc.name);
            //console.log(docApi);
            //console.log(this);
            //console.log(doc.name);
            //console.log('.list-actions button[data-name="'+ doc.name +'"]');
            //console.log($('.list-actions button[data-name="'+ doc.name +'"]').length);

            //Lograr que sea visible en mobile
            $('.list-actions').parent().removeClass('hidden-md');
            $('.list-actions').parent().removeClass('hidden-xs');
            $('.list-actions').parent().parent().removeClass('hidden-xs');
            //

            var actionButton = $('.list-actions > .btn-action[data-name="' + doc.name + '"]');

            $(actionButton).removeClass('btn-default');
            $(actionButton).addClass('btn-warning');

            $(actionButton).attr('endRender', 'true');

            $(actionButton).click(function (e) {
                e.preventDefault();
                PrepareDocumentForSend(doc);
            });

            //icon-attachment
            //icon-tool
            //icon-review
            //icon-printer
            //icon-arrow-right
            //#icon-reply
            //#icon-reply-all
            //console.log(docApi.numeroautorizacion);

            //console.log(docApi.sri_estado);
            var removeMainButton = false;

            //if ((docApi.numeroautorizacion == "" || docApi.numeroautorizacion == "0") && docApi.sri_estado != 200)
            if(true) //true cuando aun no se han implementado los campos custom - modo de desarrollo
            {
				//Continúa la renderización del botón de envío
				// ya que no se ha autorizado
            }
            else 
            {
                //Oculta el botón principal
                $(actionButton).addClass('d-none');

                // old icon version <svg class="icon icon-sm" style="">
                //<use class="" href="#icon-reply-all"></use>
                //</svg>
                //	new icon version <i class="fa fa-paper-plane"></i>
                //Se agrega el botón de envío
                $(actionButton).parent().append(`
                    <button class="btn btn-xs btn-default" data-name="` + doc.name + `" title="Enviar por email" onclick="event.stopPropagation(); document.Website.SendEmail('` + doc.name + `'); ">
    					<i class="fa fa-paper-plane"></i>
    				</button>
                `);

                removeMainButton = true;
            }

            /*
            $('.list-actions button[data-name="' + doc.name + '"]').parent().append(`
                <button class="btn btn-xs btn-default btn-download-xml" data-name="` + doc.name + `" title="Descargar Xml" onclick="event.stopPropagation(); document.Website.DownloadXml('` + doc.name + `'); ">
                    <svg class="icon icon-sm" style="">
                        <use class="" href="#icon-small-file"></use>
                    </svg>
                </button>
            `);

            $('.list-actions button[data-name="' + doc.name + '"]').parent().append(`
                <button class="btn btn-xs btn-default btn-download-pdf" data-name="` + doc.name + `" title="Descargar Pdf" onclick="event.stopPropagation(); document.Website.DownloadPdf('` + doc.name + `'); ">
                    <svg class="icon icon-sm" style="">
                        <use class="" href="#icon-printer"></use>
                    </svg>
                </button>
            `);
            */


            var buttonGroup = `<div class="dropdown show" data-name="` + doc.name + `" style="display: inline-block;position: unset !important;">
  <a class="btn btn-secondary dropdown-toggle btn-xs" href="#" role="button" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
    
  </a>
  <div class="dropdown-menu" aria-labelledby="dropdownMenuLink">
    <a class="dropdown-item" href="javascript:document.Website.DownloadXml('` + doc.name + `'); "><i class="fa fa-file-code-o" aria-hidden="true"></i> Xml ${doc.name}</a>
    <a class="dropdown-item" href="javascript:document.Website.DownloadPdf('` + doc.name + `'); "><i class="fa fa-file-pdf-o" aria-hidden="true"></i> Pdf ${doc.name}</a>
    <a class="dropdown-item" href="javascript:document.Website.ShowInfo('` + doc.name + `'); "><i class="fa fa-info-circle" aria-hidden="true"></i> Ver información</a>
  </div>
</div>
`;

            var buttonGroupExists = $('div.dropdown[data-name="' + doc.name + '"]');
            if (buttonGroupExists.length > 0) {
                //Evitamos que se renderice varias veces el botón de opciones
                return false;
            }

            $(actionButton).parent().append(buttonGroup);

            //
            if (removeMainButton) {
                //Se elimina el botón principal
                $(actionButton).remove();
            }

        }, 1000);
}

//TODO: Colocar validacide lista hasta solucionar la carga focalizada
console.log("Inicio Lista v2:" + Date().toString());

frappe.listview_settings['Sales Invoice'] = frappe.listview_settings['Sales Invoice'] || {};

frappe.listview_settings['Sales Invoice'].button = {
    show(doc) {
        //console.log("Lista:" + Date().toString());
        //return doc.status != 'Paid';

        //if (doc.status == 'Cancelled' || doc.status == 'Draft') {
        //    return false;
        //}

        SetupCustomButtons(doc);
        return true;
    },
    get_label() 
    {
        //old return __('<svg class="icon icon-sm" style=""><use class="" href="#icon-mark-as-read"></use></svg>');
        return __('<i class="fa fa-play"></i>');
    },
    get_description(doc) 
    {
        return __('Enviar al SRI')
    },
    action(doc) 
    {
        var actionButton = $('.list-actions > .btn-action[data-name="' + doc.name + '"]');
        //console.log($(actionButton).attr('endRender'));

        if ($(actionButton).attr('endRender') != 'true') {
            frappe.show_alert({
                message: __(`${doc.name} aún se está configurando, espere un momento por favor.`),
                indicator: 'red'
            }, 3);
        }
        
        //Se omite la siguiente linea porque se redunda el llamado de la funcion
        //PrepareDocumentForSend(doc);
    }
}
