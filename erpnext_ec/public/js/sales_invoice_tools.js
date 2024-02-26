function PrepareDocument(doc_name)
{
	setTimeout(
        async function ()
		{
			var docApi = await frappe.db.get_doc('Sales Invoice', doc_name);	
			
			//console.log(docApi);
			
			var sitenameVar = frappe.boot.sitename;			
			var customerApi = await frappe.db.get_doc('Customer', docApi.customer);

			//var customerAddress = null;
			//console.log(customerApi);
			//if(customerApi.customer_primary_address != null && customerApi.customer_primary_address != '')
			//{
			//	customerAddress = await frappe.db.get_doc('Address', customerApi.customer_primary_address);
				//console.log(customerAddress);
			//}
			
			var paymentsItems = null;
			var paymentsEntryApi = null;
			var paymentsEntryRefApi = await frappe.db.get_list('Payment Entry Reference', { 'fields': '["*"]', 'filters': { 'reference_name': docApi.name } });			
			//console.log(paymentsEntryRefApi);
			
			if(paymentsEntryRefApi!=null && paymentsEntryRefApi.length > 0)
			{
				//console.log(paymentsEntryRefApi[0].parent);
				var paymentsEntryApi = await frappe.db.get_list('Payment Entry', { 'fields': '["*"]', 'filters': { 'name': paymentsEntryRefApi[0].parent } });
				//console.log(paymentsEntryApi);
			}
			
			//Existe pago
			if(paymentsEntryApi!=null && paymentsEntryApi.length > 0)
			{
				console.log('Pago existente...');
				for (const paymentEntryItem of paymentsEntryApi) 
				{
					var modeOfPaymentApi = await frappe.db.get_doc('Mode of Payment', paymentEntryItem.mode_of_payment );				
					//console.log(paymentRequestItem);
					//console.log(modeOfPaymentApi);
					paymentEntryItem.formapago = modeOfPaymentApi.formapago;
					paymentEntryItem.plazo = 0;
					paymentEntryItem.Total = paymentEntryItem.paid_amount;
					paymentEntryItem.UnidadTiempo = "dias";
				}
				
				paymentsItems = paymentsEntryApi;				
			}
			else
			{
				//Sino existe pago se evaluan los requerimientos de pago
				var paymentRequestsApi = await frappe.db.get_list('Payment Request', { 'fields': '["*"]',  'filters': { 'reference_name': docApi.name } });
				console.log('Pago no existente...');
				//console.log(paymentRequestsApi);
				for (const paymentRequestItem of paymentRequestsApi) 
				{
					var modeOfPaymentApi = await frappe.db.get_doc('Mode of Payment', paymentRequestItem.mode_of_payment );				
					//console.log(paymentRequestItem);
					//console.log(modeOfPaymentApi);
					paymentRequestItem.formapago = modeOfPaymentApi.formapago;
					paymentRequestItem.plazo = 0;
					paymentRequestItem.Total = paymentRequestItem.grand_total;
					paymentRequestItem.UnidadTiempo = "dias";
				}
				
				paymentsItems = paymentRequestsApi;
			}
			
			//console.log(paymentsItems);
			
			//var modeOfPaymentApi = await frappe.db.get_list('Mode of Payment', { 'fields': '["*"]',  
			//	'filters': { 'mode_of_payment': 'Transferencia Bancaria' } });
			
			//console.log(modeOfPaymentApi);
  			//paymentRequestsApi.forEach((element) => 
			//{				
			//});
			var DireccionMatriz = '';
			var dirEstablecimiento = '';
			var direccionComprador = '';
			var emailComprador = '';
			
			var companyApi = await frappe.db.get_doc('Company', docApi.company);
			
			if(docApi.company_address != undefined)
			{			
				var companyAddressApi = await frappe.db.get_doc('Address', docApi.company_address);
				if(companyAddressApi.address_line1 == null)
					companyAddressApi.address_line1 = '';
				
				if(companyAddressApi.address_line2 == null)
					companyAddressApi.address_line2 = '';
				
				DireccionMatriz = companyAddressApi.address_line1 + ' ' + companyAddressApi.address_line2;
				dirEstablecimiento = companyAddressApi.address_line1 + ' ' + companyAddressApi.address_line2;
			}
			else
			{
				var dinLinkApi = await frappe.db.get_list('Dynamic Link', { 'fields': '["*"]','filters': { 'link_doctype': 'Company', 'parenttype':'Address' , 'link_name': docApi.company } });

                //console.log(dinLinkApi);

                if(dinLinkApi.length > 0)
                {
                    var companyAddressApi = await frappe.db.get_doc('Address', dinLinkApi[0].parent);
                    
                    if(companyAddressApi.address_line1 == null)
                        companyAddressApi.address_line1 = '';
                    
                    if(companyAddressApi.address_line2 == null)
                        companyAddressApi.address_line2 = '';
                    
                    DireccionMatriz = companyAddressApi.address_line1 + ' ' + companyAddressApi.address_line2;
                    dirEstablecimiento = companyAddressApi.address_line1 + ' ' + companyAddressApi.address_line2;
                }
				
			}
			
			console.log(docApi.customer_address);

			if(docApi.customer_address != undefined)
			{
				var customerAddressApi = await frappe.db.get_doc('Address', docApi.customer_address);
				direccionComprador = customerAddressApi.address_title;
				emailComprador = customerAddressApi.email_id;
			}
			else
			{
				var dinLinkApiC = await frappe.db.get_list('Dynamic Link', { 'fields': '["*"]','filters': { 'link_doctype': 'Customer', 'parenttype':'Address' , 'link_name': docApi.customer } });
                if(dinLinkApiC.length > 0)
                {
                    var customerAddressApi = await frappe.db.get_doc('Address', dinLinkApiC[0].parent);
                    direccionComprador = customerAddressApi.address_title;
                    emailComprador = customerAddressApi.email_id;
                }
			}
			
			docApi.DireccionMatriz = DireccionMatriz;
			docApi.dirEstablecimiento = dirEstablecimiento;
			docApi.direccionComprador = direccionComprador;
			docApi.emailComprador = direccionComprador;
				
			var commentsApi = await frappe.db.get_list('Comment', { 'fields': '["*"]','filters': { 'reference_name': docApi.name } });
			
			docApi.company_name = companyApi.company_name;
			docApi.nombreComercial = companyApi.nombrecomercial;
			docApi.agenteRetencion = companyApi.agenteretencion;
			docApi.contribuyenteEspecial = companyApi.contribuyenteespecial;
			docApi.obligadoContabilidad = companyApi.obligadocontabilidad;
			docApi.contribuyenteRimpe = companyApi.contribuyenterimpe;			
			docApi.paymentsItems = paymentsItems;			
			
			const typeidtax = '';

            if(customerApi.typeidtax != undefined)
            {
                typeidtax = customerApi.typeidtax.split(' ');
                docApi.tipoIdentificacionComprador = typeidtax[0];
            }
			//console.log(customerApi);
			
			if(docApi.taxes!=null && docApi.taxes.length > 0)
			{
				console.log('Taxes existente...');
				for (const taxItem of docApi.taxes) 
				{
					var accountApi = await frappe.db.get_doc('Account', taxItem.account_head );				
					//console.log(accountApi);
					
					taxItem.sricode = accountApi.sricode;
					taxItem.codigoPorcentaje = accountApi.sricodeper;
					
				}
				
				paymentsItems = paymentsEntryApi;				
			}
			
			var strComment = BuildComment(commentsApi);
			
            var customer_email_id = '';
            var customer_phone = '';

            if(customerAddressApi != undefined)
            {
                if( customerAddressApi.email_id  != undefined)
                {
                    customer_email_id = customerAddressApi.email_id;
                }

                if( customerAddressApi.phone != undefined)
                {
                    customer_phone = customerAddressApi.phone;
                }
            }

			infoAdicionalData = "";
            infoAdicionalData = [{
									"nombre":"email",
									"valor": customer_email_id
								 },
								 {
									"nombre":"tel.",
									"valor": customer_phone
								 },
								 {
									"nombre":"Doc. Ref.",
									"valor":docApi.name
								 },
								 {
									"nombre":"Coment.",
									"valor":strComment
								 }
								];
								
			docApi.infoAdicional = infoAdicionalData;
			//console.log(infoAdicionalData);
			
			
			console.log(docApi);
			console.log(JSON.stringify(docApi));
			//console.log(companyAddressApi);
			//console.log(customerAddressApi);			
			//console.log(companyApi);
			//console.log(paymentRequestsApi);
			
			
		var url = `${btApiServer}/api/Download/xmlfromjson/?tip_doc=FAC&sitename=`;
        var req = new XMLHttpRequest();
        req.open("POST", url, true);
        req.responseType = "blob";
        /*
        req.loadend = function (event) {
            console.log('Terminado');
            $(btnProcess).show();
            $(btnProcess).parent().find('.custom-animation').remove();
        };
        */
        req.onload = function (event) {
            //console.log(req);
            var fileNameForDownload = doc + `.${typeFile}`;
            var disposition = req.getResponseHeader('Content-Disposition');
            //console.log(disposition);
            if (disposition && disposition.indexOf('attachment') !== -1) {
                var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                var matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) {
                    fileNameForDownload = matches[1].replace(/['"]/g, '');
                }
            }

            var blob = req.response;
            //var fileName = req.getResponseHeader("fileName") //if you have the fileName header available
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = fileNameForDownload;
            link.click();

            //console.log('Terminado');
            $(btnProcess).show();
            $(btnProcess).parent().find('.custom-animation').remove();
        };

        //req.send(JSON.stringify(docApi));
			
		}, 100);
}


function SendSalesInvoice(doc) {
    setTimeout(
        async function () {


			var properties_view = Object.getOwnPropertyNames(frappe.views.list_view);
			var doctype_erpnext = properties_view[0];

			console.log(doctype_erpnext);
            console.log(doc);

            var sitenameVar = frappe.boot.sitename;
			var customer_email_id = '';
			
            var customerApi = await frappe.db.get_doc('Customer', doc.customer);
            console.log(customerApi);

			var customerAddress = null;			

			if(customerApi.customer_primary_address != null && customerApi.customer_primary_address != '')
			{
				customerAddress = await frappe.db.get_doc('Address', customerApi.customer_primary_address);
				//console.log(customerAddress);
			}

            var paymentsApi = await frappe.db.get_list('Payment Request', { 'filters': { 'reference_name': doc.name } });
            //console.log(paymentsApi);
            //TODO: Arreglar/Verificar el error que da la siguiente linea
            //var paymentsEntryApi = await frappe.db.get_list('Payment Entry Reference', { 'filters': { 'reference_name': doc.name }, fields: ['name'], order_by: null });
            // se reemplaza hasta solucionarlo

            var paymentsEntryApi = await frappe.db.get_list('Payment Request', { 'filters': { 'reference_name': doc.name } });

            //console.log(paymentsEntryApi);

            var docApi = frappe.get_doc('Sales Invoice', doc.name);
            var data_alert = '<table>';
            //console.log(docApi);
            var documentIsReady = true;

            if (paymentsApi.length == 0 && paymentsEntryApi.length == 0) {
                data_alert += document.Website.CreateAlertItem(`No se ha definido ni solicitud de pago ni entrada de pago`);
                documentIsReady = false;
            }

            //if(docApi.tax_id == "" || docApi.tax_id == "9999999999")
            //{
            //data_alert += `<span class="indicator-pill red ellipsis">
            //    <span class="ellipsis"> Cédula/Ruc del cliente es ${docApi.tax_id}</span>
            //</span>`;
            //}

            if (customerApi.tax_id == "" || customerApi.tax_id == "9999999999") {
                data_alert += document.Website.CreateAlertItem(`Cédula/Ruc del cliente es ${customerApi.tax_id}`);
            }
			
			if (customerAddress == null) {
                data_alert += document.Website.CreateAlertItem(`No se han definido datos de dirección del cliente`);
				documentIsReady = false;
            }			
			
			if (customerAddress != null && (customerAddress.email_id == "" || customerAddress.email_id == null )) {
                data_alert += document.Website.CreateAlertItem(`No se ha definido Email del cliente`);
				documentIsReady = false;
            }
			
			if (customerAddress != null)
			{
				customer_email_id = customerAddress.email_id;
			}

			console.log(docApi.estab);

            if (docApi.estab == null || docApi.estab == '' || docApi.estab == undefined) {
                data_alert += document.Website.CreateAlertItem(`Establecimiento incorrecto (${docApi.estab})`);
                documentIsReady = false;
            }
			else
			{
				data_alert += document.Website.CreateHtmlItem(`Establecimiento (${docApi.estab})`, 'green');
			}

			console.log(docApi.ptoemi);

            if (docApi.ptoemi == null || docApi.ptoemi == '' || docApi.ptoemi == undefined) {
                data_alert += document.Website.CreateAlertItem(`Punto de emisión incorrecto (${docApi.ptoemi})`);
                documentIsReady = false;
            }
			else
			{
				data_alert += document.Website.CreateHtmlItem(`Punto de emisión (${docApi.ptoemi})`, 'green');
			}

            data_alert += '</table>'

            //await frappe.db.get_doc('Customer', 'CONSUMIDOR FINAL')

            var document_preview = `
            <p>Confirmar para procesar el documento ${doc.name}</p>
            <table>
                <tr>
                    <td>Nombre cliente:</td>
                    <td>${doc.customer_name}</td>
                </tr>
                <tr>
                    <td>Tip.Doc. cliente:</td>
                    <td>${customerApi.typeidtax}</td>
                </tr>
                <tr>
                    <td>Cédula/RUC cliente:</td>
                    <td>${customerApi.tax_id}</td>
                </tr>
				<tr>
                    <td>Email cliente:</td>
                    <td>${customer_email_id}</td>
                </tr>
            </table>
            ` + data_alert +
                `<div class="warning-sri">Por favor, verifique que toda la información esté correctamente ingresada antes de enviarla al SRI y generar el documento electrónico.</div>`;

			//if (documentIsReady)
            if (true)
			{

                frappe.warn('Enviar al SRI?',
                    document_preview,
                    () => {

                        frappe.show_alert({
                            message: __(`Documento ${doc.name} está siendo procesado en el SRI, por favor espere un momento. `),
                            indicator: 'green'
                        }, 7);

                        var btnProcess = $('.list-actions button[data-name="' + doc.name + '"]').parent().find('.btn-action');
                        //Oculta el botón
                        $(btnProcess).hide();
                        //Muestra animación de carga
                        $(btnProcess).after(document.Website.loadingAnimation);

                        // action to perform if Yes is selected
                        console.log('Enviando al SRI');
                        //console.log(doc);
                        var docApi = frappe.get_doc('Sales Invoice', doc.name);
                        //console.log(docApi);
						
						typeDocSri = '-';

						if(doctype_erpnext == 'Sales Invoice')
							typeDocSri = 'FAC';
				
						if(doctype_erpnext == 'Delivery Note')
							typeDocSri = 'GRS';

						frappe.call({
							method: "erpnext_ec.utilities.sri_ws.send_doc",
							args: 
							{
								doc: doc,
								typeDocSri: typeDocSri,
								doctype_erpnext: doctype_erpnext,
								siteName: sitenameVar,
								freeze: true,
								freeze_message: "Procesando documento, espere un momento.",
								success: function(r) {},								
								always: function(r) {},
							},
							callback: function(r) 
							{
								//console.log(r);

								jsonResponse = JSON.parse(r.message);
								console.log(jsonResponse);

								//console.log(json_data.data.claveAccesoConsultada);
								//console.log(json_data.data.autorizaciones.autorizacion[0].numeroAutorizacion);
								
								if(jsonResponse.ok && jsonResponse.data.numeroComprobantes > 0)
								{		
									//console.log(req);
									//console.log(req.responseText)

									//var stringResponse = req.responseText;
									//stringResponse = stringResponse.replace(/(<([^>]+)>)/gi, '');											
									//const jsonResponse = JSON.parse(stringResponse);
									var newNumeroAutorizacion = jsonResponse.data.autorizaciones.autorizacion[0].numeroAutorizacion;

									//var newNumeroAutorizacion = '000010000100000100001010101010FAKE';
									// old icon version <use class="" href="#icon-reply-all"></use>
									//	new icon version <i class="fa fa-paper-plane"></i>
									$(btnProcess).parent().find('.custom-animation').remove();
									$(btnProcess).parent().append(`
									<button class="btn btn-xs btn-default" data-name="` + doc.name + `" title="Enviar por email" onclick="event.stopPropagation(); document.Website.SendEmail('` + doc.name + `'); ">                					
										<i class="fa fa-paper-plane"></i></button>`);

									frappe.show_alert({
										message: __(`Documento ${doc.name} procesado <br>Nueva clave de acceso SRI: ` + newNumeroAutorizacion),
										indicator: 'green'
									}, 5);

									if(jsonResponse.error!==undefined && jsonResponse.error !== '')
									{
										var string_error = jsonResponse.error;
										frappe.show_alert({
											message: __(string_error),
											indicator: 'red'
										}, 10);
									}

									//bye bye!!
									return;

								} 
								else 
								{
									//MOSTRAR EL MENSAJE DE ERROR MAS DETALLADO
									//console.log(req);
									//console.log("Error", req.statusText);
									//console.log('1x');
									var string_error = jsonResponse.error;
									var string_informacionAdicional = '';
									var string_mensaje = '';
									try
									{
										string_error = jsonResponse.error;
										string_mensaje = jsonResponse.data.autorizaciones.autorizacion[0].mensajes.mensaje[0].mensaje_;
										string_informacionAdicional = jsonResponse.data.autorizaciones.autorizacion[0].mensajes.mensaje[0].informacionAdicional;										 
									}
									catch(ex_messages)
									{

									}

									frappe.show_alert({
										message: __(`Error al procesar documento ${doc.name}:` + string_error + ":" + string_mensaje + ":" + string_informacionAdicional),
										indicator: 'red'
									}, 10);
								}

								//console.log('Terminado proceso con el SRI!');
								$(btnProcess).show();
								$(btnProcess).parent().find('.custom-animation').remove();                            	
								
								/*
								if(r.message)
								{
									let root_company = r.message.length ? r.message[0] : "";
									me.page.fields_dict.root_company.set_value(root_company);
			
									frappe.db.get_value("Company", {"name": company}, "allow_account_creation_against_child_company", (r) => {
										frappe.flags.ignore_root_company_validation = r.allow_account_creation_against_child_company;
									});
								}
								*/
							},
							error: function(r) {
								$(btnProcess).show();
								$(btnProcess).parent().find('.custom-animation').remove();
							},
						});
						
					//},);

                    },
                    'Confirmar proceso de envío al SRI'
                );
            }
            else {

				//Cuando la factura no esté correcta
                frappe.msgprint({
                    title: __('Factura incompatible con el SRI'),
                    indicator: 'red',
                    message: __(document_preview)
                });
            }


        }, 100);
}