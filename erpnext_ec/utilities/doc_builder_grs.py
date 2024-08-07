import frappe
from frappe import _
import erpnext
import json
from datetime import timedelta
from types import SimpleNamespace
from erpnext_ec.utilities.doc_builder_tools import *
from erpnext_ec.utilities.doc_render_tools import *

@frappe.whitelist()
def build_doc_grs_with_images(doc_name):
	doc_response = build_doc_grs(doc_name)
	if(not doc_response.numeroautorizacion):
		doc_response.numeroautorizacion = "0"	
	doc_response.numeroautorizacion_img = get_barcode_base64(doc_response.numeroautorizacion)
	doc_response.logo_img = get_barcode_base64(doc_response.numeroautorizacion)
	#print(doc_response.numeroautorizacion_img)
	return doc_response

#Guía de remisión
@frappe.whitelist()
def build_doc_grs(doc_name):
	# DireccionMatriz = ''
	# dirEstablecimiento = ''
	# direccionComprador = ''
	# emailComprador = ''	
    
	docs = frappe.get_all('Delivery Note', filters={"name": doc_name}, fields = ['*'])
	customer_email_id =  ''

	sri_validated = 'ok';
	sri_validated_message = ''

	if docs:
		doc = docs[0]		
		doc.items = get_full_items_delivery_note(doc.name)
		
		#Datos completos de la compañia emisora
		company_full = get_full_company_sri(doc.company)

		#print('Compañia')
		#print(company_full)
		
		doc.razonSocial = company_full['razonSocial'] #La razon social es el nombre normal de la empresa emisora
		doc.nombreComercial = company_full['nombreComercial']
		doc.company_name = doc.company
		
		doc.tax_id = company_full['ruc']
		doc.DireccionMatriz = company_full['dirMatriz']
		doc.dirEstablecimiento = company_full['dirMatriz'] # TODO: temporal, la dirección del establecimiento debe ser definida
		doc.contribuyenteRimpe = company_full['contribuyenteRimpe']
		doc.obligadoContabilidad = company_full['obligadoContabilidad']
		doc.agenteRetencion = company_full['agenteRetencion']
		doc.contribuyenteEspecial = company_full['contribuyenteEspecial']
		doc.ambiente = company_full['ambiente']		

		#Datos completos del cliente
		customer_full = get_full_customer_sri(doc.customer)
		doc.customer_tax_id = customer_full['customer_tax_id']		
		doc.tipoIdentificacionComprador = customer_full['tipoIdentificacionComprador']
		doc.direccionComprador = customer_full['direccionComprador']
		customer_phone = customer_full['customer_phone']
		customer_email_id = customer_full['customer_email_id']

		doc.infoAdicional = build_infoAdicional_sri(doc_name, customer_email_id, customer_phone)

		# Obtener datos de entrega desde delivery trip y stops

		doc.deliveryTrips = get_full_delivery_trips(doc)

		placa_vehiculo = ""
		conductor_nombre = ""
		
		destinatarios = []
		for deliveryTripItem in doc.deliveryTrips:
			placa_vehiculo = deliveryTripItem.vehicle
			conductor_nombre = deliveryTripItem.driver_name
			fechaInicioTransporte = deliveryTripItem.departure_time

			for driverItem in deliveryTripItem.trip_driver:
				print(driverItem.transporter)
				supplier_trip = frappe.get_all('Supplier', filters={'name': driverItem.transporter}, fields=['*'])
				print(supplier_trip)
				if(supplier_trip):
					for supplierItem in supplier_trip:
						#print (supplierItem.tax_id)
						razonSocialTransportista = supplierItem.name
						tipoIdentificacionTransportista = supplierItem.typeidtax
						rucTransportista = supplierItem.tax_id

						doc.razonSocialTransportista = razonSocialTransportista
						doc.tipoIdentificacionTransportista = tipoIdentificacionTransportista
						doc.rucTransportista = rucTransportista
						break
				break

			for deliveryStopItem in deliveryTripItem.delivery_stops:
				detalles = []

				for itemDetalle in doc['items']:
					detalles.append(
								{
								"codigoInterno": itemDetalle.item_code,
								"descripcion": itemDetalle.description,
								"cantidad": itemDetalle.qty
							})
				if(not deliveryStopItem.docaduanerounico):
					deliveryStopItem.docaduanerounico = '000'
				
				if(not deliveryStopItem.customerestablishment):
					deliveryStopItem.customerestablishment = '001'

				#sales_invoice_docs = frappe.get_all('Sales Invoice', filters={"docidsri": deliveryStopItem.numDocSustento.strip()}, fields = ['*']) 
				#numAutDocSustento = ''
				#if(len(sales_invoice_docs) > 0):
				#	numAutDocSustento = sales_invoice_docs[0].numeroautorizacion

				new_destinatarios = {
					"identificacionDestinatario": doc.customer_tax_id,
					"razonSocialDestinatario": doc.customer_name.upper().strip(),
					"dirDestinatario": deliveryStopItem.dirDestinatario.upper().strip(),
					"motivoTraslado": deliveryStopItem.motivotraslado.upper().strip(),										
					"docAduaneroUnico": deliveryStopItem.docaduanerounico,
					"codEstabDestino": deliveryStopItem.customerestablishment,
					"ruta": deliveryStopItem.ruta,
					"codDocSustento": "01",
					"numDocSustento": deliveryStopItem.numDocSustento.strip(),
					"numAutDocSustento": deliveryStopItem.numAutDocSustento.strip(),
					"fechaEmisionDocSustento": doc.posting_date.strftime("%d/%m/%Y"),					
					"detalles" : {"detalle": detalles}
				}
			
				destinatarios.append(new_destinatarios)

		doc.destinatarios = destinatarios
		doc.placa_vehiculo = placa_vehiculo
		doc.conductor_nombre = conductor_nombre

		doc.fechaInicioTransporte = fechaInicioTransporte

		# print(doc.infoAdicional)

		#Simulando error
		sri_validated = 'error'
		sri_validated_message += 'Cliente requerido-'
		sri_validated_message += 'No se han definido datos de dirección del cliente-'
		sri_validated_message += 'No se ha definido Email del cliente-'
		sri_validated_message += 'Establecimiento incorrecto-'
		sri_validated_message += 'Punto de emisión incorrecto-'
		sri_validated_message += 'No se ha definido ni solicitud de pago ni entrada de pago-'
		#Simulando error-----------fin

		if sri_validated == 'ok':
			sri_validated_message = 'Listo!';
		
		doc.sri_validated = sri_validated
		doc.sri_validated_message = sri_validated_message

		if(not doc.secuencial or doc.secuencial == 0):
			new_secuencial = setSecuencial(doc, 'GRS')
			if new_secuencial > 0:
				doc.secuencial = new_secuencial			

		tipoDocumento = '06'
		tipoAmbiente = doc.ambiente
		tipoEmision = 1

		fechaEmision = doc.posting_date
		puntoEmision = doc.ptoemi
		secuencial = doc.secuencial
		ruc = doc.tax_id
		establecimiento = doc.estab		

		claveAcceso = GenerarClaveAcceso(tipoDocumento, 
                                     fechaEmision, 
                                     puntoEmision, 
                                     secuencial, 
                                     tipoEmision, 
									ruc,
									tipoAmbiente,
									establecimiento)
		
		print(f'Clave de acceso creada: {claveAcceso}')

		doc.claveAcceso = claveAcceso
		doc.numeroautorizacion = claveAcceso

		return doc


def build_doc_grs_sri(data_object):
	
	#print(data_object)
	#return ""

	#print(data_object['items'])

	infoAdicional = []
	for infoAdicionalItem in data_object.infoAdicional:
		if(infoAdicionalItem['valor']):
			infoAdicional.append(
			{
				"nombre": infoAdicionalItem['nombre'],
				"valor": infoAdicionalItem['valor'].upper()
			})

	obligadoContabilidad = 'NO'
	if(data_object.obligadoContabilidad == 1):
		obligadoContabilidad = 'SI'

	contribuyenteRimpe = "CONTRIBUYENTE RÉGIMEN RIMPE"
	if(data_object.contribuyenteRimpe != 1):
		contribuyenteRimpe = ""

	#Se asigna datos de emisor en caso de que no haya transportista asignado
	if(not data_object.razonSocialTransportista):
		data_object.razonSocialTransportista = data_object.razonSocial.upper().strip() #data_object.razonSocial
		data_object.tipoIdentificacionTransportista = '04' #'04'
		data_object.rucTransportista = data_object.tax_id #data_object.tax_id

	data = {
        "infoTributaria": {
            "ambiente": data_object.ambiente,
            "tipoEmision": "1",
            "razonSocial": data_object.razonSocial.upper().strip(),
            "nombreComercial": data_object.nombreComercial.upper().strip(),
            "ruc": data_object.tax_id,
            "claveAcceso": data_object.claveAcceso,
            "codDoc": "06",
            "estab" : data_object.estab,
            "ptoEmi" : data_object.ptoemi,
            "secuencial" : '{:09d}'.format(data_object.secuencial),
            "dirMatriz" : data_object.DireccionMatriz.upper().strip(),
			"contribuyenteRimpe": contribuyenteRimpe			
        },
        "infoGuiaRemision": {
            #"fechaEmision": data_object.posting_date.strftime("%d/%m/%Y"), # data_object.posting_date,			
			#"dirEstablecimiento": data_object.dirEstablecimiento.upper(),
			"dirPartida": data_object.dirEstablecimiento.upper().strip(),
			"razonSocialTransportista": data_object.razonSocialTransportista.upper().strip(),
			"tipoIdentificacionTransportista": data_object.tipoIdentificacionTransportista,
			"rucTransportista": data_object.rucTransportista,
			"obligadoContabilidad": obligadoContabilidad,
			"contribuyenteEspecial": data_object.contribuyenteEspecial,
			#"fecha": data_object.posting_date.strftime("%d/%m/%Y"),
			"fechaIniTransporte": data_object.fechaInicioTransporte.strftime("%d/%m/%Y"), #"01/04/2024",
        	"fechaFinTransporte":(data_object.fechaInicioTransporte + timedelta(days=1)).strftime("%d/%m/%Y"),
        	"placa": data_object.placa_vehiculo,
			#"rise":"Contribuyente Regimen Simplificado RISE",            
            #"tipoIdentificacionComprador": data_object.tipoIdentificacionComprador			
        },
        "destinatarios": {
            "destinatario": data_object.destinatarios
        },
        "infoAdicional": {
            "campoAdicional": infoAdicional
        }
    }

	return data
