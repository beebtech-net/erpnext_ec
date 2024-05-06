function PrepareDocumentForSendV2(doc, DocTypeErpNext)
{
	switch(DocTypeErpNext)
	{
		case 'Sales Invoice':
			{
				console.log('MEtodo Facturas de venta');
				SendSalesInvoice(doc);
			}
			break;
		case 'Delivery Note':
			{
				console.log('MEtodo Guia de remision');
				SendDeliveryNote(doc);
			}
			break;
		case 'Purchase Withholding Sri Ec':
			{
				console.log('MEtodo COmprobante de Retencion');
			}
			break;
	}

	console.log(DocTypeErpNext);
}


function SetupCustomButtons(doc, DocTypeErpNext)
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
            var docApi = await frappe.db.get_doc(DocTypeErpNext, doc.name);
            
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
                //PrepareDocumentForSend(doc);
				PrepareDocumentForSendV2(doc, DocTypeErpNext);
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

			if(allowSendSri(docApi))
            //if ((docApi.numeroautorizacion == null || docApi.numeroautorizacion == "" || docApi.numeroautorizacion == "0") && docApi.sri_estado != 200)
            //if(true) //true cuando aun no se han implementado los campos custom - modo de desarrollo
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

            var buttonGroup = `<div class="dropdown show" data-name="` + doc.name + `" style="display: inline-block;position: unset !important;">
  <a class="btn btn-secondary dropdown-toggle btn-xs" href="#" role="button" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
  </a>
  <div class="dropdown-menu" aria-labelledby="dropdownMenuLink">
    <a class="dropdown-item" href="javascript:document.Website.DownloadXml_v2('` + doc.name + `'); "><i class="fa fa-file-code-o" aria-hidden="true"></i> Xml ${doc.name}</a>
	<a class="dropdown-item" href="javascript:document.Website.DownloadPdf_v2('` + doc.name + `'); "><i class="fa fa-file-pdf-o" aria-hidden="true"></i> Pdf ${doc.name}</a>    
    <a class="dropdown-item hide" href="javascript:document.Website.DownloadXml('` + doc.name + `'); "><i class="fa fa-file-code-o" aria-hidden="true"></i> Xml ${doc.name}</a>
    <a class="dropdown-item hide" href="javascript:document.Website.DownloadPdf('` + doc.name + `'); "><i class="fa fa-file-pdf-o" aria-hidden="true"></i> Pdf ${doc.name}</a>
    <div class="dropdown-divider documentation-links"></div>
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

function SetListSriButtons(DocTypeErpNext)
{
	//
	//TODO: Colocar validacide lista hasta solucionar la carga focalizada
	console.log("Inicio Lista v2:" + Date().toString());

	frappe.listview_settings[DocTypeErpNext] = frappe.listview_settings[DocTypeErpNext] || {};

	frappe.listview_settings[DocTypeErpNext].button = {
		show(doc) 
		{
			//console.log("Lista:" + Date().toString());
			//return doc.status != 'Paid';

			//if (doc.status == 'Cancelled' || doc.status == 'Draft') {
			//    return false;
			//}

			SetupCustomButtons(doc,DocTypeErpNext);
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
}

function allowSendSri(docApi)
{
	if ((docApi.numeroautorizacion == null || docApi.numeroautorizacion == "" || docApi.numeroautorizacion == "0") && docApi.sri_estado != 200)
	{
		return true;
	}
	else
	{
		return false;
	}
}

function SetFormSriButtons(frm, DocTypeErpNext)
{
	//console.log('allowSendSri');
	//console.log(allowSendSri(frm.doc));

	if(allowSendSri(frm.doc))
	{
		frm.add_custom_button(__('<i class="fa fa-play"></i> Enviar al SRI'), function() {
			// When this button is clicked, do this            
			console.log(frm.doc);
			console.log("Cargado Script add_custom_button ----cambiado");
			var subject = frm.doc.subject;
			var event_type = frm.doc.event_type;
			//PrepareDocumentForSend(frm.doc);
			PrepareDocumentForSendV2(frm.doc, DocTypeErpNext);
		},);
	}

	frm.add_custom_button(__('<i class="fa fa-file-code-o"></i> Descargar XML'), function() 
	{
		//frappe.show_alert({
		//	message: __(`${frm.doc.name} Implementación requerida.`),
		//	indicator: 'red'
		//}, 3);

		//console.log('DOC NAMEEEEEEEEEEE');
		//console.log(frm.doc.name);

		//document.Website.DownloadXml('` + frm.doc.name + `');
		document.Website.DownloadXml_v2(frm.doc.name);

	},__('<svg class="icon  icon-sm" style=""><use class="" href="#icon-organization"></use></svg>Sri')); //NO SOPORTA AWESOME ICONS

	frm.add_custom_button(__('<i class="fa fa-file-pdf-o"></i> Descargar PDF'), function() 
	{		
		document.Website.DownloadPdf_v2(frm.doc.name);
	},__('<svg class="icon  icon-sm" style=""><use class="" href="#icon-organization"></use></svg>Sri'));
}

async function GetFullCompanySri(def_company)
{
	//Variable de retorno
	var companiaSri = {};

	//var def_company = frappe.defaults.get_user_default("Company");
	//frappe.defaults.get_user_default("Company") || frappe.defaults.get_global_default("company")

	var docs = await frappe.db.get_list('Company', { 'fields': '["*"]', 'filters': { 'name': def_company } });
	console.log(docs);
		
	if(docs.length > 0)
	{
		companiaSri.nombreComercial = docs[0].nombrecomercial;
		companiaSri.ruc = docs[0].tax_id;
		companiaSri.obligadoContabilidad = docs[0].obligadocontabilidad;			

		var company_address_primary = null;
		var company_address_first = null;

		//TODO: Revisar filtro - NO FUNCIONA  -- [BUG][?]
		var dinLinkApi = await frappe.db.get_list('Dynamic Link',{ 'fields': '["name","parent","link_title"]', 'filters' : {'link_doctype': 'Company', 'parenttype':'Address' ,'link_name':def_company}})
		console.log(dinLinkApi);
			
		if(dinLinkApi.length > 0)
		{
			foundPrimary = false;
			for (let i = 0; i < dinLinkApi.length; i++)
			{
				var company_address = await frappe.db.get_list('Address',{ 'fields': '["*"]', 'filters' : {'name': dinLinkApi[i].parent}});
					
				console.log(company_address);

				if(company_address.length > 0)
				{

					if(i == 1)
					{
						company_address_first = company_address[0];
					}

					if(company_address[0].is_primary_address)
					{
						//console.log("Primaria!");
						//console.log(company_address[0]);
						foundPrimary = true;
						company_address_primary = company_address[0];
					}
				}					

				if(foundPrimary)
				{
					break;
				}
			}

			if(!foundPrimary)
			{
				company_address_primary = company_address_first;
			}
		}

		console.log(company_address_primary);

		if(company_address_primary!=null)
		{
			companiaSri.dirMatriz = company_address_primary.address_line1;
		}

		console.log(companiaSri);
		return companiaSri;			
	}	
}