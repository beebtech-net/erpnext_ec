import frappe
from frappe import _
import erpnext
import json
from types import SimpleNamespace
from erpnext_ec.utilities.doc_builder_tools import *
from erpnext_ec.utilities.doc_render_tools import *

@frappe.whitelist()
def build_doc_liq_with_images(doc_name):
	doc_response = build_doc_liq(doc_name)
	doc_response.numeroautorizacion_img = get_barcode_base64(doc_response.numeroautorizacion)
	doc_response.logo_img = get_barcode_base64(doc_response.numeroautorizacion)
	return doc_response

#Factura de Venta
@frappe.whitelist()
def build_doc_liq(doc_name):
	
	# DireccionMatriz = ''
	# dirEstablecimiento = ''
	# direccionComprador = ''
	# emailComprador = ''	
    
	docs = frappe.get_all('Purchase Invoice', filters={"name": doc_name}, fields = ['*'])
	customer_email_id =  ''

	sri_validated = 'ok';
	sri_validated_message = ''

	if docs:
		doc = docs[0]
		
		doc.taxes = get_full_taxes_purchases(doc.name)
		#print("TAXEEESSS")
		#print(doc.taxes)
  
		#print("ITEEEEMMMMSSSS")
		doc.items = get_full_items_purchase_invoice(doc.name, doc)
		#print(doc.items)

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

		#print('doc.purchase_withholding_supplier')
		#print(doc.supplier)
		#Datos completos del proveedor
		supplier_full = get_full_supplier_sri(doc.supplier)
		#print(supplier_full)

		supplier_phone = ''
		supplier_email_id = ''
		
		if(supplier_full):
			doc.razonSocialProveedor = supplier_full['supplier_name']
			doc.identificacionProveedor = supplier_full['supplier_tax_id']
			doc.tipoIdentificacionProveedor = supplier_full['tipoIdentificacionProveedor']
			doc.direccionProveedor = supplier_full['direccionProveedor']
			supplier_phone = supplier_full['supplier_phone']
			supplier_email_id = supplier_full['supplier_email_id']

		doc.supplier_phone = supplier_phone
		doc.supplier_email_id = supplier_email_id

		doc.paymentsItems = get_payments_sri(doc.name)
		doc.pagos = build_pagos(doc.paymentsItems)

		doc.infoAdicional = build_infoAdicional_sri(doc_name, supplier_email_id, supplier_phone)

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
			new_secuencial = setSecuencial(doc, 'LIQ')
			if new_secuencial > 0:
				doc.secuencial = new_secuencial			

		tipoDocumento = '03'
		tipoAmbiente = doc.ambiente
		tipoEmision = 1

		fechaEmision = doc.posting_date		
		secuencial = doc.secuencial
		ruc = doc.tax_id #doc.company_tax_id
		
		puntoEmision_rec = get_full_ptoemi(doc.ptoemi)
		doc.ptoemi = puntoEmision_rec.record_name
		puntoEmision = doc.ptoemi
		
		establecimiento_rec = get_full_establishment(doc.estab)
		doc.estab = establecimiento_rec.record_name
		establecimiento = doc.estab

		if(ruc == None):
			ruc = '0000000000000'

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

def build_doc_liq_sri(data_object):

	totalConImpuestos = []

	for taxItem in data_object.taxes:
		totalConImpuestos.append({
			"totalImpuesto": {
						"codigo": taxItem.sricode,
						"codigoPorcentaje": taxItem.codigoPorcentaje,
						"baseImponible": "{:.2f}".format(taxItem.baseImponible),
						"tarifa": "{:.2f}".format(taxItem.rate),
						"valor": "{:.2f}".format(taxItem.tax_amount)
					}
		})

	#print(data_object['items'])

	detalles = []

	for item in data_object['items']:

		#print(item)
		impuestos = []

		for impuesto in item.impuestos:
			#print(impuesto)

			impuestos.append({
					"impuesto": {
						"codigo": impuesto['codigo'],
						"codigoPorcentaje": impuesto['codigoPorcentaje'],
						"tarifa": "{:.2f}".format(impuesto['tarifa']),
						"baseImponible": "{:.2f}".format(impuesto['baseImponible']),
						"valor": "{:.2f}".format(impuesto['valor']) #impuesto['valor']
					}})

		#ErpNext coloca descuento negativo cuando el precio es modificado a un precio mas alto
		# es decir , llena el campo discount_amount pero no el discount_percentage
		#if (item.discount_amount < 0 and item.discount_percentage == 0):
		#	item.discount_amount = 0

		detalles.append({
                "codigoPrincipal": item.item_code,
                "descripcion": item.description.upper(),
                "cantidad": item.qty,
                "precioUnitario": "{:.2f}".format(item.precioUnitario),
                "descuento": "{:.2f}".format(item.qty * item.discount_amount),
                "precioTotalSinImpuesto": "{:.2f}".format(item.precioTotalSinImpuesto),
                "impuestos": impuestos                
            })

	infoAdicional = []
	for infoAdicionalItem in data_object.infoAdicional:
		if(infoAdicionalItem['valor']):
			infoAdicional.append(
			{
				"nombre": infoAdicionalItem['nombre'],
				"valor": infoAdicionalItem['valor'].upper()
			})
	
	pagos = []
	#print(data_object.pagos)
	
	for pagoItem in data_object.pagos:
		pagos.append({
					"pago":
					{
						"formaPago": pagoItem['formaPago'],
						"total": "{:.2f}".format(pagoItem['total']),
						"plazo": pagoItem['plazo'],
						"unidadTiempo": pagoItem['unidadTiempo']
					}})

	#print(pagos)

	obligadoContabilidad = 'NO'
	if(data_object.obligadoContabilidad == 1):
		obligadoContabilidad = 'SI'
	
	agenteRetencion = None
	if(not data_object.agenteRetencion == None and 
		not data_object.agenteRetencion == '' and
		not data_object.agenteRetencion == '0'):
		agenteRetencion = data_object.agenteRetencion

	contribuyenteRimpe = "CONTRIBUYENTE RÉGIMEN RIMPE"
	if(data_object.contribuyenteRimpe != 1):
		contribuyenteRimpe = ""

	data = {
        "infoTributaria": {
            "ambiente": data_object.ambiente,
            "tipoEmision": "1",
            "razonSocial": data_object.razonSocial.upper(),
            "nombreComercial": data_object.nombreComercial.upper(),
            "ruc": data_object.tax_id,
            "claveAcceso": data_object.claveAcceso,
            "codDoc": "03",
            "estab" : data_object.estab,
            "ptoEmi" : data_object.ptoemi,
            "secuencial" : '{:09d}'.format(data_object.secuencial),
            "dirMatriz" : data_object.DireccionMatriz.upper(),
			"agenteRetencion": agenteRetencion,
			"contribuyenteRimpe": contribuyenteRimpe
        },
        "infoLiquidacionCompra": {
            "fechaEmision": data_object.posting_date.strftime("%d/%m/%Y"), # data_object.posting_date,
            "dirEstablecimiento": data_object.dirEstablecimiento.upper(),
            "contribuyenteEspecial": data_object.contribuyenteEspecial,
            "obligadoContabilidad": obligadoContabilidad,
            "tipoIdentificacionProveedor": data_object.tipoIdentificacionProveedor,
            "razonSocialProveedor": data_object.razonSocialProveedor.upper(),
            "identificacionProveedor": data_object.identificacionProveedor,
			"direccionProveedor": data_object.direccionProveedor,
            "totalSinImpuestos": "{:.2f}".format(data_object.base_total),
            "totalDescuento": "{:.2f}".format(data_object.discount_amount),
			"codDocReembolso": "00",
			"totalComprobantesReembolso": data_object.grand_total,
			"totalBaseImponibleReembolso": data_object.grand_total,
			"totalImpuestoReembolso": data_object.grand_total,
            "totalConImpuestos": totalConImpuestos,
            "importeTotal": data_object.grand_total,
            "moneda": "DOLAR",
            "pagos": pagos
        },
        "detalles": {
            "detalle": detalles
        },
        "infoAdicional": {
            "campoAdicional": infoAdicional
        }
    }

	return data
