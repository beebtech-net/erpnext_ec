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
		doc.items = get_full_items(doc.name)
		
		print(doc)
		print(doc.items)
        
		doc.taxes = get_full_taxes_withhold(doc.name)

		#print(doc.company)
		#print(doc)
		#Datos completos de la compañia emisora
		company_full = get_full_company_sri(doc.company)		

		doc.nombreComercial = company_full['nombreComercial']
		doc.company_name = doc.company
		
		doc.tax_id = company_full['ruc']
		doc.DireccionMatriz = company_full['dirMatriz']
		doc.dirEstablecimiento = company_full['dirMatriz'] # TODO: temporal, la dirección del establecimiento debe ser definida
		doc.contribuyenteRimpe = company_full['contribuyenteRimpe']
		
		#Datos completos del cliente
		supplier_full = get_full_supplier_sri(doc.purchase_withholding_supplier)
		print(supplier_full)

		doc.supplier_tax_id = supplier_full['supplier_tax_id']
		doc.RazonSocial = supplier_full['supplier_name']
		doc.tipoIdentificacionSujetoRetenido = supplier_full['tipoIdentificacionProveedor']
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
		return doc
	
	#Sino es encontrado
	return None