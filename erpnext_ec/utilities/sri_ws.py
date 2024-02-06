# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

#from erpnext_ec.erpnext_ec.doctype import xml_responses

from datetime import datetime
import time
import frappe
from frappe import _
import erpnext
#from frappe.utils.pdf import get_pdf

import json
from types import SimpleNamespace
import requests
from erpnext_ec.utilities.encryption import encrypt_string

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# from bson import json_util
# import json

import re

def build_comment(comments):
	str_comment = ''
	for comment in comments:
		# print(comment)
		str_comment = comment.get('content', '')
		str_comment = strip_html(str_comment)
		str_comment = normalize_string(str_comment)
		break  # Sale del bucle después de procesar el primer comentario
    
    # Aquí puedes manejar si str_comment está vacío después del bucle
    # if not str_comment:
    #     pass
	return str_comment

def strip_html(input_string):
    """Elimina todas las etiquetas HTML de una cadena."""
    return re.sub('<[^>]*>', '', input_string)

def normalize_string(source_str):
    """Normaliza una cadena eliminando caracteres especiales y espacios extra."""
    try:
        normalized_str = source_str.strip()
        normalized_str = re.sub('[^a-zA-Z0-9 ]+', '', normalized_str.normalize('NFD'))
    except Exception as e:
        print('Error: NormalizeString')
        print('Data: ' + source_str)
        # Aquí puedes manejar el error según tus necesidades
        normalized_str = source_str  # Considera devolver la cadena original o manejar de otra manera
    return normalized_str


def build_infoAdicional_sri(doc_name, customer_email_id, customer_phone):

	commentsApi = frappe.get_all('Comment', filters = { 'reference_name': doc_name }, fields='*' );
	# print('COMENTAAAAAARIOOOOOOSSSSSS')
	# print(commentsApi)

	strComment = build_comment(commentsApi)

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
							"valor":doc_name
							},
							{
							"nombre":"Coment.",
							"valor":strComment
							}
						];

	return infoAdicionalData

def get_payments_sri(doc_name):
	sri_validated = ''
	sri_validated_message = ''
      
	paymentsEntryApi = frappe.get_list('Payment Entry Reference', filters = { 'reference_name': doc_name })
	# print(paymentsEntryApi)

	if not paymentsEntryApi:
		paymentsApi = frappe.get_list('Payment Request', filters = { 'reference_name': doc_name })
		# print(paymentsApi)

		if not paymentsApi and  not paymentsEntryApi:
			sri_validated = 'error'
			sri_validated_message += 'No se ha definido ni solicitud de pago ni entrada de pago-'
		else:
			return paymentsApi
	else:
		return paymentsEntryApi
	
	return None

def get_full_company_sri(def_company):
    # Variable de retorno
    compania_sri = {}

    # Obteniendo la compañía por defecto si def_company es None
    # def_company = def_company or frappe.defaults.get_user_default("Company")

    docs = frappe.get_all('Company', fields='*', filters={'name': def_company})
    #print(docs)
    
    if docs:
        doc = docs[0]
        compania_sri['nombreComercial'] = doc.nombrecomercial
        compania_sri['ruc'] = doc.tax_id
        compania_sri['obligadoContabilidad'] = doc.obligadocontabilidad

        company_address_primary = None
        company_address_first = None

        din_link_api = frappe.get_all('Dynamic Link', fields='["name","parent","link_title"]',
                                                filters={'link_doctype': 'Company', 'parenttype': 'Address', 'link_name': def_company})
        #print(din_link_api)

        if din_link_api:
            found_primary = False
            for i, link in enumerate(din_link_api):
                company_address = frappe.get_all('Address', fields='*', filters={'name': link.parent})
                # print(company_address)

                if company_address:
                    if i == 0:
                        company_address_first = company_address[0]

                    if company_address[0].get('is_primary_address'):
                        found_primary = True
                        company_address_primary = company_address[0]
                        break

            if not found_primary and company_address_first:
                company_address_primary = company_address_first

        #print(company_address_primary)

        if company_address_primary:
            compania_sri['dirMatriz'] = company_address_primary.address_line1

        #print(compania_sri)
        return compania_sri
	

def get_full_customer_sri(def_customer):
    # Variable de retorno
    customer_sri = {}

    # Obteniendo la compañía por defecto si def_company es None
    # def_company = def_company or frappe.defaults.get_user_default("Company")

    docs = frappe.get_all('Customer', fields='*', filters={'name': def_customer})    
    
    if docs:
        doc = docs[0]
        # print(doc)
        customer_sri['customer_tax_id'] = doc.tax_id
        customer_sri['customer_name'] = doc.nombrecomercial
        customer_sri['tipoIdentificacionComprador'] = doc.typeidtax
        customer_sri['customer_email_id']  = ''
        customer_sri['customer_phone']  = ''

        customer_address_primary = None
        customer_address_first = None

        din_link_api = frappe.get_all('Dynamic Link', fields='["name","parent","link_title"]',
                                                filters={'link_doctype': 'Customer', 'parenttype': 'Address', 'link_name': def_customer})
        # print('DIRECCCCCCCCCCIIIIIIIONNNNNNN CUSTOMMMMERRRR')
        # print(din_link_api)

        if din_link_api:
            found_primary = False
            for i, link in enumerate(din_link_api):
                customer_address = frappe.get_all('Address', fields='*', filters={'name': link.parent})
                #print(customer_address)

                if customer_address:
                    if i == 0:
                        customer_address_first = customer_address[0]

                    if customer_address[0].get('is_primary_address'):
                        found_primary = True
                        customer_address_primary = customer_address[0]
                        break

            if not found_primary and customer_address_first:
                customer_address_primary = customer_address_first
        else:
            #Sino se encuentra una dirección vinculada se busca una direccion primaria del cliente
            customer_address = frappe.get_all('Address', fields='*', filters={'name': docs.customer_primary_address})
            if customer_address:
                customer_address_primary = customer_address[0]
            else:
                print('---')
				
        if customer_address_primary:
            customer_sri['customer_email_id']  = customer_address_primary.email_id
            customer_sri['customer_phone']  = customer_address_primary.phone

        #print(compania_sri)
        return customer_sri

def get_full_items(doc_name):    
    items = frappe.get_all('Sales Invoice Item',
                           filters={'parent': doc_name},
                           fields=['*']
                        #    fields=['item_code', 'item_name', 'rate', 'qty', 'amount']
                                       )

    return items

def get_full_taxes(doc_name):    
    
	impuestos = frappe.get_all('Sales Taxes and Charges', filters={'parent': doc_name}, fields=['*'])
    #    fields=['charge_type', 'account_head', 'tax_amount']
	
	for taxItem in impuestos:
		accountApi = frappe.get_doc('Account', taxItem.account_head)
		# print('CUENTAAAAAAAAAAAAA')
		# print(accountApi)
		# print(accountApi.sricode)
		# print(accountApi.sricodeper)

		if accountApi.sricode:
			taxItem.sricode =  int(accountApi.sricode)
              
		if accountApi.sricodeper:
			taxItem.codigoPorcentaje = int(accountApi.sricodeper)

	return impuestos

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


@frappe.whitelist()
def get_doc(doc_name, typeDocSri, typeFile, siteName):

	# print(doc_name, typeDocSri, typeFile, siteName)

	#El parametro doc aquí es el nombre del documento

	doc = build_doc_fac(doc_name)
	#print(doc_name)
	#print(doc.customer_email_id)

	#print(doc.sri_validated)
	#print(doc.sri_validated_message)

	doc_str = json.dumps(doc, default=str)
	#print(doc_str)

	#json -> object
	# x = json.loads(doc, object_hook=lambda d: SimpleNamespace(**d))
	# print("get_doc")
	# print(x.name)
	
	#headers = { "Authorization" : "our_unique_secret_token" }
	headers = {}

	# data = {
	# 	"id": 1001,
	# 	"name": "geek",
	# 	"passion": "coding",
	# }
	
	api_url = f"https://192.168.204.66:7037/api/v2/Download/{typeFile}?documentName={doc_name}&tip_doc={typeDocSri}&sitename={siteName}"
	
	#response = requests.post(api_url, json=doc_str, verify=False, stream=True, headers= headers)
	response = requests.post(api_url, data=doc_str, verify=False, stream=True, headers= headers)
	
	#for k,v in r.raw.headers.items(): print(f"{k}: {v}")
	#print(r.text)
	#print(response)
	#print(response.text)
	
	#html = '<h1>Invoice from Star Electronics e-Store!</h1>'

    # Add items to PDF HTML
	#html += '<ol>'	
	#html += '<li>item 1</li>'
	#html += '</ol>'

	#print(get_pdf(html))

    # Attaching PDF to response
	#frappe.response.filename = 'invoice.pdf'
	#frappe.response.filecontent = get_pdf(html)
	#frappe.response.type = 'pdf'
	
	#frappe.throw(_('You need to have "Share" permission'), frappe.PermissionError)
	#raise Exception("Sorry, no numbers below zero")

	return response.text

@frappe.whitelist()
def send_doc(doc):	

	activation_level = 0
	sales_data = []
	min_count = 0
	doctypes = {
		"Asset": 5,		
		"Customer": 5,
		"Delivery Note": 5,		
		"Item": 5,
		"Journal Entry": 3,
		"Lead": 3,
		"Payment Entry": 2,		
		"Purchase Order": 2,
		"Purchase Invoice": 5,
		"Purchase Receipt": 5,		
		"Sales Order": 2,
		"Sales Invoice": 2,
		"Stock Entry": 3,
		"Supplier": 5		
	}

	# for doctype, min_count in doctypes.items():
	# 	count = frappe.db.count(doctype)
	# 	if count > min_count:
	# 		activation_level += 1
	# 	sales_data.append({doctype: count})

	# if frappe.db.get_single_value("System Settings", "setup_complete"):
	# 	activation_level += 1

	# communication_number = frappe.db.count("Communication", dict(communication_medium="Email"))
	# if communication_number > 10:
	# 	activation_level += 1
	# sales_data.append({"Communication": communication_number})

	# # recent login
	# if frappe.db.sql(
	# 	"select name from tabUser where last_login > date_sub(now(), interval 2 day) limit 1"
	# ):
	# 	activation_level += 1

	# level = {"activation_level": activation_level, "sales_data": sales_data}
	
	#print(doc)

	x = json.loads(doc, object_hook=lambda d: SimpleNamespace(**d))
	print("DESDE OBJETO")
	print(x.name)

	level = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
	#time.sleep(5)
	level += '   RESPUESTA SRI   ' # + doc.name
	level += datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

	#Se agrega un nuevo Xml Response para que se lance el evento y se envie el email
	xml_response_new = frappe.get_doc({
		'id': 1,
        'doctype': 'Xml Responses',
        'description': "[Description]", #f"{doc.name} Added",        
    })

	xml_response_new.insert()
	frappe.db.commit()

	#Preparar documento enviarlo al servicio externo de autorización
	#---------------------------------------------------------------
	
	#api_url = "http://localhost:3003/api/Download/xml/MAT-DT-2023-00065?tip_doc=GRS&sitename=hdc"
	
	#url para simulacion de SRI
	#api_url = "http://67.225.226.30:3003/api/Tool/Simulate"
	api_url = "http://localhost:7037/api/Tool/Simulate"
	
	response = requests.post(api_url, verify=False, stream=True)
	#for k,v in r.raw.headers.items(): print(f"{k}: {v}")
	#print(r.text)
	
	#print(response.text);
	#print(response.status_code);
	
	response_json = json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))

	if(response.status_code):
		#evaluar estado de respuesta SRI
		if(response_json.ok and int(response_json.data.numeroComprobantes) > 0):
			print ("correcto")

			#proceder a actualizar datos del registro	
			print(response_json.data.claveAccesoConsultada)
			print(response_json.data.numeroComprobantes)
			print(response_json.data.autorizaciones.autorizacion[0].estado)
			print(response_json.data.autorizaciones.autorizacion[0].numeroAutorizacion)
			print(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)
			print(response_json.data.autorizaciones.autorizacion[0].ambiente)

			signature_object = frappe.get_last_doc('Sri Signature', filters = { 'tax_id': '091982695800111'})
			#signature_object = frappe.get_doc('Sri Signature','EXP-2024-00097')

			if(signature_object):
				print(signature_object)
				print(signature_object.Firma)

				if(signature_object.Firma):
					input_data = signature_object.Firma

					key = "ratonratonquequieresgatoladron.." #32 bytes

					encrypted_data = encrypt_string(input_data, key)
					print("p12 encriptado")
					print(encrypted_data)

					input_pwd = "ronaldpassword"
					encrypted_pwd = encrypt_string(input_pwd, key)
					print("pwd encriptado")
					print(encrypted_pwd)

	#api_url = "https://jsonplaceholder.typicode.com/todos/10"
	#response = requests.get(api_url)
	
	#print(response.json());

	#{'userId': 1, 'id': 10, 'title': 'illo est ... aut', 'completed': True}

	#todo = {"userId": 1, "title": "Wash car", "completed": True}
	#response = requests.put(api_url, json=todo)
	#print(response.json())
	#{'userId': 1, 'title': 'Wash car', 'completed': True, 'id': 10}

	#frappe.msgprint(f"{xml_response_new.id} has been created.")

	return response.text