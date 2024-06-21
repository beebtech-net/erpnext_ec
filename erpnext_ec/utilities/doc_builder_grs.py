import frappe
from frappe import _
import erpnext
import json
from types import SimpleNamespace
from erpnext_ec.utilities.doc_builder_tools import *

#Guía de remisión
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

				new_destinatarios = {
					"identificacionDestinatario": doc.customer_tax_id,
					"razonSocialDestinatario": doc.customer_name.upper().strip(),
					"dirDestinatario": deliveryStopItem.dirDestinatario.upper().strip(),
					"motivoTraslado": deliveryStopItem.motivotraslado.upper().strip(),
					"codDocSustento": "01", #deliveryStopItem.numAutDocSustento,
					"numDocSustento": deliveryStopItem.numDocSustento.strip(),
					"fechaEmisionDocSustento": doc.posting_date.strftime("%d/%m/%Y"),
					"detalles" : {"detalle": detalles}
				}
			
				destinatarios.append(new_destinatarios)

		doc.destinatarios = destinatarios
		doc.placa_vehiculo = placa_vehiculo
		doc.conductor_nombre = conductor_nombre

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
			"fechaIniTransporte": "01/04/2024",
        	"fechaFinTransporte":" 01/04/2024",
        	"placa": data_object.placa_vehiculo,
			#"rise":"Contribuyente Regimen Simplificado RISE",

            "contribuyenteEspecial": data_object.contribuyenteEspecial,
            "obligadoContabilidad": obligadoContabilidad,
            "tipoIdentificacionComprador": data_object.tipoIdentificacionComprador,            
        },
        "destinatarios": {
            "destinatario": data_object.destinatarios
        },
        "infoAdicional": {
            "campoAdicional": infoAdicional
        }
    }

	return data
