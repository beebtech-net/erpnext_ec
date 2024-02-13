import frappe
from frappe import _
import erpnext
import json
from types import SimpleNamespace
from erpnext_ec.utilities.doc_builder_tools import *

#Factura de Venta
def build_doc_fac(doc_name):
	# DireccionMatriz = ''
	# dirEstablecimiento = ''
	# direccionComprador = ''
	# emailComprador = ''	
    
	docs = frappe.get_all('Sales Invoice', filters={"name": doc_name}, fields = ['*'])
	customer_email_id =  ''

	sri_validated = 'ok';
	sri_validated_message = ''

	if docs:
		doc = docs[0]
		#print("ITEEEEMMMMSSSS")
		doc.items = get_full_items(doc.name)
		#print(doc.items)
        
		doc.taxes = get_full_taxes(doc.name)
		#print("TAXEEESSS")
		#print(doc.taxes)

		#Datos completos de la compañia emisora
		company_full = get_full_company_sri(doc.company)

		#print('Compañia')
		#print(company_full)

		doc.nombreComercial = company_full['nombreComercial']
		doc.company_name = doc.company
		
		doc.tax_id = company_full['ruc']
		doc.DireccionMatriz = company_full['dirMatriz']
		doc.dirEstablecimiento = company_full['dirMatriz'] # TODO: temporal, la dirección del establecimiento debe ser definida

		#Datos completos del cliente
		customer_full = get_full_customer_sri(doc.customer)
		doc.customer_tax_id = customer_full['customer_tax_id']
		doc.RazonSocial = customer_full['customer_name']
		doc.tipoIdentificacionComprador = customer_full['tipoIdentificacionComprador']
		customer_phone = customer_full['customer_phone']
		customer_email_id = customer_full['customer_email_id']


		# 		if customerAddress:
		# 			emailComprador = customerAddress[0].email_id
		# 			doc.customer_email_id = emailComprador
		# 		else:
		# 			sri_validated = 'error'
		# 			sri_validated_message += 'No se ha definido Email del cliente-'
		# 	else:
		# 		sri_validated = 'error'
		# 		sri_validated_message += 'No se han definido datos de dirección del cliente-'
		# else:
		# 	sri_validated = 'error'
		# 	sri_validated_message += 'Cliente requerido'

		# 	if not paymentsApi and  not paymentsEntryApi:
		# 		sri_validated = 'error'
		# 		sri_validated_message += 'No se ha definido ni solicitud de pago ni entrada de pago-'

		doc.paymentsItems = get_payments_sri(doc.name)

		doc.infoAdicional = build_infoAdicional_sri(doc_name, customer_email_id, customer_phone)

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
		return doc
