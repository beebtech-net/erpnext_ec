/***********************************/
function resolveFromExternal(r, doc, btnProcess)
{
	console.log(r);


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
}

function resolveFromInternal(r, doc, btnProcess)
{
	var r___ = {
		"message": {
				"claveAccesoConsultada": "2803202401091982695800110010020000001701234567818",
				"numeroComprobantes": "1",
				"autorizaciones": {
					"autorizacion": {
						"estado": "NO AUTORIZADO",
						"fechaAutorizacion": "2024-05-05T15:31:45-05:00",
						"ambiente": "PRUEBAS",
						"comprobante": "<factura id=\"comprobante\" version=\"1.1.0\"></factura>",
						"mensajes": {
							"mensaje": {
								"identificador": "58",
								"mensaje": "ERROR EN LA ESTRUCTURA DE LA CLAVE DE ACCESO",
								"informacionAdicional": "La clave de acceso 2803202401091982695800110010020000001701234567818 no cumple módulo 11",
								"tipo": "ERROR"
							}
						}								
				}				
			},
			"ok": true
		}
	}

	console.log(r);

	jsonResponse = r.message;
	console.log(jsonResponse);

	if(jsonResponse.data != undefined)
	{
		//jsonResponse = jsonResponse.data;
	}

	//console.log(json_data.data.claveAccesoConsultada);
	//console.log(json_data.data.autorizaciones.autorizacion[0].numeroAutorizacion);
	
	if(jsonResponse.numeroComprobantes > 0)
	{
		if(jsonResponse.autorizaciones.autorizacion.estado == 'AUTORIZADO')
		{
			var newNumeroAutorizacion = jsonResponse.autorizaciones.autorizacion.numeroAutorizacion;

			$(btnProcess).parent().find('.custom-animation').remove();
			$(btnProcess).parent().append(`
			<button class="btn btn-xs btn-default" data-name="` + doc.name + `" title="Enviar por email" onclick="event.stopPropagation(); document.Website.SendEmail('` + doc.name + `'); ">                					
				<i class="fa fa-paper-plane"></i></button>`);

			var alert_message = `Documento ${doc.name} procesado <br>Nueva clave de acceso SRI: ` + newNumeroAutorizacion;
			
			if(!jsonResponse.ok)
			{
				alert_message = jsonResponse.custom_info;
			}

			frappe.show_alert({
				message: __(alert_message),
				indicator: 'green'
			}, 5);
			
			return;
		}
		//if(jsonResponse.autorizaciones.autorizacion.estado == 'NO AUTORIZADO')
		else
		{
			//if(jsonResponse.autorizaciones.autorizacion.mensajes.mensaje.tipo = "ERROR")
			//{
				var string_error = 
				jsonResponse.autorizaciones.autorizacion.estado + ":" +
				jsonResponse.autorizaciones.autorizacion.mensajes.mensaje.identificador + ":" +
				jsonResponse.autorizaciones.autorizacion.mensajes.mensaje.mensaje + ":" +
				jsonResponse.autorizaciones.autorizacion.mensajes.mensaje.informacionAdicional;
				frappe.show_alert({
					message: __(string_error),
					indicator: 'red'
				}, 10);
			//}
		}
		
		//console.log('DATOS DE ERROR');
		//console.log(jsonResponse.error);

		//Se mostrará alerta de error en este nivel solamente si es que
		// jsonResponse.error contiene información que deba ser mostrada
		//if(jsonResponse.error!==null && jsonResponse.error!==undefined && jsonResponse.error !== '')
		//{
		//	var string_error = jsonResponse.error;
		//	frappe.show_alert({
		//		message: __(string_error),
		//		indicator: 'red'
		//	}, 10);
		//}

		//return;
	}
	else 
	{
		//MOSTRAR EL MENSAJE DE ERROR MAS DETALLADO
		
		var string_error = ''; //jsonResponse.error;
		var string_informacionAdicional = '';
		var string_mensaje = '';
		try
		{
				if(jsonResponse.custom_info != undefined)
				{
					string_error = jsonResponse.custom_info;
				}

			//string_error = jsonResponse.error;
			if(jsonResponse.comprobantes != undefined)
			{
				string_mensaje = jsonResponse.comprobantes.comprobante.mensajes.mensaje.mensaje;
				string_informacionAdicional = jsonResponse.comprobantes.comprobante.mensajes.mensaje.informacionAdicional;

				string_error = string_error == null ? '' : string_error;
				string_mensaje = string_mensaje == null ? '' : string_mensaje;
				string_informacionAdicional = string_informacionAdicional == null ? '' : string_informacionAdicional;
			}

			if(jsonResponse.autorizacion != undefined)
			{				
				string_mensaje = jsonResponse.autorizaciones.autorizacion.mensajes.mensaje.mensaje;
				string_informacionAdicional = jsonResponse.autorizaciones.autorizacion.mensajes.mensaje.informacionAdicional;										 

				string_error = string_error == null ? '' : string_error;
				string_mensaje = string_mensaje == null ? '' : string_mensaje;
				string_informacionAdicional = string_informacionAdicional == null ? '' : string_informacionAdicional;
			}

			
		}
		catch(ex_messages)
		{
			
		}

		frappe.show_alert({
			message: __(`Error al procesar documento l2 - ${doc.name}:` + string_error + ":" + string_mensaje + ":" + string_informacionAdicional),
			indicator: 'red'
		}, 10);
	}

	//console.log('Terminado proceso con el SRI!');
	$(btnProcess).show();
	$(btnProcess).parent().find('.custom-animation').remove();  
}

function SendSalesInvoiceToSri(documentIsReady, document_preview, doc)
{
	var doctype_erpnext = 'Sales Invoice';
	var typeDocSri = 'FAC';
	var documentName = 'Factura';
    var sitenameVar = frappe.boot.sitename;

	console.log(doc.is_return);
	console.log(doc.status);
	//"Return"
	//evaluar si es nota de crédito
	if(doc.is_return)
	{
		typeDocSri = 'NCR';
		documentName = 'Nota de Crédito';
	}
	
	if (documentIsReady)
	{
		frappe.warn('Enviar ' + documentName + ' al SRI?',
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
				//resolveFromInternal(null, doc, btnProcess);
				//return;	

				frappe.call({
					method: "erpnext_ec.utilities.sri_ws.send_doc_native",
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
						//resolveFromExternal(r, doc, btnProcess);
						resolveFromInternal(r, doc, btnProcess);
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
			title: __(documentName + ' incompatible con el SRI'),
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
			doc_name: doc.name,
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
            <p>Confirmar para procesar el documento ${doc.name}</p>` + 
			data_header +
			data_alert +
                `<div class="warning-sri">Por favor, verifique que toda la información esté correctamente ingresada antes de enviarla al SRI y generar el documento electrónico.</div>`;

			SendSalesInvoiceToSri(r.message.documentIsReady, document_preview, doc);

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
	validationSri(doc);
}

