import frappe
from frappe import _
import erpnext
import json
from types import SimpleNamespace
from erpnext_ec.utilities.doc_builder_tools import *

#Comprobante de retencion
def build_doc_cre(doc_name):
	# DireccionMatriz = ''
	# dirEstablecimiento = ''
	# direccionComprador = ''
	# emailComprador = ''	
    
	docs = frappe.get_all('Purchase Withholding Sri Ec', filters={"name": doc_name}, fields = ['*'])
	supplier_email_id =  ''

	sri_validated = 'ok';
	sri_validated_message = ''

	if docs:
		doc = docs[0]
		#print("ITEEEEMMMMSSSS")
		#doc.items = get_full_items(doc.name)
		
		#print(doc)
		#print(doc.items)
        
		doc.impuestos = get_full_taxes_withhold(doc.name)

		#print(doc.company)
		#print(doc)
		#Datos completos de la compañia emisora
		company_full = get_full_company_sri(doc.company)		

		doc.razonSocial = company_full['razonSocial']
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
		supplier_full = get_full_supplier_sri(doc.purchase_withholding_supplier)
		#print(supplier_full)

		doc.supplier_tax_id = supplier_full['supplier_tax_id']		
		doc.tipoIdentificacionSujetoRetenido = supplier_full['tipoIdentificacionProveedor']
		#doc.direccionComprador = supplier_full['direccionProveedor']
		supplier_phone = supplier_full['supplier_phone']
		supplier_email_id = supplier_full['supplier_email_id']

		doc.paymentsItems = get_payments_sri(doc.name)

		doc.infoAdicional = build_infoAdicional_sri(doc_name, supplier_email_id, supplier_phone)

		# print(doc.infoAdicional)

		#Simulando error
		sri_validated = 'error'
		sri_validated_message += 'Proveedor requerido-'
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
			new_secuencial = setSecuencial(doc, 'CRE')
			if new_secuencial > 0:
				doc.secuencial = new_secuencial			

		tipoDocumento = '07'
		tipoAmbiente = doc.ambiente
		tipoEmision = 1

		fechaEmision = doc.fechaEmision
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
	
	#Sino es encontrado
	return None

def build_doc_cre_sri(data_object):
	print("----------------------------------------------")
	print(data_object)
	print("----------------------------------------------")
	#return ""

	impuestos = []

	for taxItem in data_object.impuestos:
		#fechaEmisionDocSustento = datetime.strptime(fecha_string, "%Y-%m-%dT%H:%M:%S")
		
		impuestos.append({			
			"codigo": taxItem.codigoRetencionId,
			"codigoRetencion": taxItem.codigoRetencionId,
			"baseImponible": "{:.2f}".format(taxItem.baseImponible),
			"porcentajeRetener": "{:.2f}".format(taxItem.porcentajeRetener),
			"valorRetenido": "{:.2f}".format(taxItem.valorRetenido),
			"codDocSustento": taxItem.codDocSustento,
			"numDocSustento": taxItem.numDocSustento.replace('-',''),
			"fechaEmisionDocSustento": taxItem.fechaEmisionDocSustento.strftime("%d/%m/%Y")
		})

	infoAdicional = []
	for infoAdicionalItem in data_object.infoAdicional:
		if(infoAdicionalItem['valor']):
			infoAdicional.append(
			{
				"nombre": infoAdicionalItem['nombre'],
				"valor": infoAdicionalItem['valor'].upper()
			})
	
	#print(pagos)

	obligadoContabilidad = 'NO'
	if(data_object.obligadoContabilidad == 1):
		obligadoContabilidad = 'SI'
	
	agenteRetencion = None
	contribuyenteRimpe = "CONTRIBUYENTE RÉGIMEN RIMPE"
	codDoc = "07"

	data = {
        "infoTributaria": {
            "ambiente": data_object.ambiente,
            "tipoEmision": "1",
            "razonSocial": data_object.razonSocial.upper(),
            "nombreComercial": data_object.nombreComercial.upper(),
            "ruc": data_object.tax_id,
            "claveAcceso": data_object.claveAcceso,
            "codDoc": codDoc,
            "estab" : data_object.estab,
            "ptoEmi" : data_object.ptoemi,
            "secuencial" : '{:09d}'.format(data_object.secuencial),
            "dirMatriz" : data_object.DireccionMatriz.upper(),
			"contribuyenteRimpe": contribuyenteRimpe,
			#"agenteRetencion": agenteRetencion
        },
        "infoCompRetencion": {
            "fechaEmision": data_object.fechaEmision.strftime("%d/%m/%Y"), # data_object.posting_date,
            #"dirEstablecimiento": data_object.dirEstablecimiento.upper(),
            #"contribuyenteEspecial": data_object.contribuyenteEspecial,
            "obligadoContabilidad": obligadoContabilidad,
            "tipoIdentificacionSujetoRetenido": data_object.tipoIdentificacionSujetoRetenido,
            "razonSocialSujetoRetenido": data_object.razonSocialSujetoRetenido.upper(),
            "identificacionSujetoRetenido": data_object.identificacionSujetoRetenido,
            "periodoFiscal":"05/2024"
        },
        "impuestos": {
            "impuesto": impuestos
        },
        "infoAdicional": {
            "campoAdicional": infoAdicional
        }
    }

	return data
