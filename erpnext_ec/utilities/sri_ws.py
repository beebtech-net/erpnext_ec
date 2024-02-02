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

@frappe.whitelist()
def get_doc(doc, typeDocSri, typeFile, siteName):
	#El parametro doc aquí es el nombre del documento

	#json -> object
	#x = json.loads(doc, object_hook=lambda d: SimpleNamespace(**d))
	#print("get_doc")
	#print(x.name)
	
	#headers = { "Authorization" : "our_unique_secret_token" }
	headers = {}

	data = {
		"id": 1001,
		"name": "geek",
		"passion": "coding",
	}
	
	api_url = f"http://localhost:3003/api/Download/{typeFile}/MAT-DT-2023-00065?tip_doc=GRS&sitename=hdc"
	
	response = requests.post(api_url, json=data, verify=False, stream=True, headers= headers)
	
	#for k,v in r.raw.headers.items(): print(f"{k}: {v}")
	#print(r.text)
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
		"BOM": 3,
		"Customer": 5,
		"Delivery Note": 5,
		"Employee": 3,
		"Issue": 5,
		"Item": 5,
		"Journal Entry": 3,
		"Lead": 3,
		"Material Request": 5,
		"Opportunity": 5,
		"Payment Entry": 2,
		"Project": 5,
		"Purchase Order": 2,
		"Purchase Invoice": 5,
		"Purchase Receipt": 5,
		"Quotation": 3,
		"Sales Order": 2,
		"Sales Invoice": 2,
		"Stock Entry": 3,
		"Supplier": 5,
		"Task": 5,
		"User": 5,
		"Work Order": 5,
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
	api_url = "http://67.225.226.30:3003/api/Tool/Simulate"
	
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
