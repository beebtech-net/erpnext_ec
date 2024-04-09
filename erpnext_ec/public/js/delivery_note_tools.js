function SendDeliveryNote(doc) {
    setTimeout(
        async function () {

			//var doctype_erpnext = get_current_doc_type()[0];
        	//var typeDocSri = get_current_doc_type()[1];
			
			var doctype_erpnext = 'Delivery Note';
        	var typeDocSri = 'GRS';

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

            var docApi = frappe.get_doc('Delivery Note', doc.name);
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
                        //var docApi = frappe.get_doc('Sales Invoice', doc.name);
                        //console.log(docApi);
						
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