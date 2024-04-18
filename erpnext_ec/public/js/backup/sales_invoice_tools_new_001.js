/***********************************/

function SendSalesInvoiceToSri(documentIsReady, document_preview)
{
	var doctype_erpnext = 'Sales Invoice';
	var typeDocSri = 'FAC';
    var sitenameVar = frappe.boot.sitename;

	if (documentIsReady)
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
				//console.log('Enviando al SRI');
								
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
							var newNumeroAutorizacion = jsonResponse.data.autorizaciones.autorizacion[0].numeroAutorizacion;

							$(btnProcess).parent().find('.custom-animation').remove();
							$(btnProcess).parent().append(`
							<button class="btn btn-xs btn-default" data-name="` + doc.name + `" title="Enviar por email" onclick="event.stopPropagation(); document.Website.SendEmail('` + doc.name + `'); ">                					
								<i class="fa fa-paper-plane"></i></button>`);

							frappe.show_alert({
								message: __(`Documento ${doc.name} procesado <br>Nueva clave de acceso SRI: ` + newNumeroAutorizacion),
								indicator: 'green'
							}, 5);
							
							console.log('DATOS DE ERROR');
							console.log(jsonResponse.error);

							//Se mostrará alerta de error en este nivel solamente si es que
							// jsonResponse.error contiene información que deba ser mostrada
							if(jsonResponse.error!==null && jsonResponse.error!==undefined && jsonResponse.error !== '')
							{
								var string_error = jsonResponse.error;
								frappe.show_alert({
									message: __(string_error),
									indicator: 'red'
								}, 10);
							}

							return;
						}
						else 
						{
							//MOSTRAR EL MENSAJE DE ERROR MAS DETALLADO
							
							var string_error = jsonResponse.error;
							var string_informacionAdicional = '';
							var string_mensaje = '';
							try
							{
								string_error = jsonResponse.error;
								string_mensaje = jsonResponse.data.autorizaciones.autorizacion[0].mensajes.mensaje[0].mensaje_;
								string_informacionAdicional = jsonResponse.data.autorizaciones.autorizacion[0].mensajes.mensaje[0].informacionAdicional;										 

								string_error = string_error == null ? '' : string_error;
								string_mensaje = string_mensaje == null ? '' : string_mensaje;
								string_informacionAdicional = string_informacionAdicional == null ? '' : string_informacionAdicional;
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
			},
			'Confirmar proceso de envío al SRI'
		);
	}
	else 
	{
		//Cuando la factura no esté correcta
		frappe.msgprint({
			title: __('Factura incompatible con el SRI'),
			indicator: 'red',
			message: __(document_preview)
		});
	}
}

function validationSri(doc)
{
	frappe.call({
		method: "erpnext_ec.utilities.doc_validator.validate_sales_invoice",
		args: 
		{
			doc_name: doc,
			freeze: false,
			freeze_message: "Procesando documento, espere un momento.",
			success: function(r) {},								
			always: function(r) {},
		},
		callback: function(r) 
		{
			console.log(r);			
			console.log(r.message.doctype_erpnext);
			//jsonResponse = JSON.parse(r.message);
			//console.log(jsonResponse);
			
			var data_header = '<table>';

			for(i=0; i < r.message.header.length; i++)
			{				
				data_header += `
				<tr>
                    <td>${r.message.header[i].description}:</td>
                    <td>${r.message.header[i].value}</td>
                </tr>
				`;
			}

			data_header += '</table>'

			var data_alert = '<table>';

			for(i=0; i < r.message.alerts.length; i++)
			{				
				data_alert += document.Website.CreateAlertItem(r.message.alerts[i].description);
			}

			data_alert += '</table>'

			console.log(data_alert);

			var document_preview = `
            <p>Confirmar para procesar el documento ${doc}</p>` + 
			data_header +
			data_alert +
                `<div class="warning-sri">Por favor, verifique que toda la información esté correctamente ingresada antes de enviarla al SRI y generar el documento electrónico.</div>`;

			SendSalesInvoiceToSri(r.message.documentIsReady, document_preview);

			//if(r.message.documentIsReady)
			//{				
			//}
		},
		error: function(r) {
			$(btnProcess).show();
			$(btnProcess).parent().find('.custom-animation').remove();
		},
	});
}

function SendSalesInvoice(doc) 
{
	validationSri(doc.name);
}

