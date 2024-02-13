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

from erpnext_ec.utilities.doc_builder_fac import build_doc_fac 
from erpnext_ec.utilities.doc_builder_grs import build_doc_grs
from erpnext_ec.utilities.doc_builder_cre import build_doc_cre

@frappe.whitelist()
def get_doc(doc_name, typeDocSri, typeFile, siteName):

	#El parametro doc aquí es el nombre del documento
      
	match typeDocSri:
		case "FAC":
			doc = build_doc_fac(doc_name)
			print ("")
		case "GRS":
			doc = build_doc_grs(doc_name)
		case "CRE":
			doc = build_doc_cre(doc_name)
	
	# print(doc_name, typeDocSri, typeFile, siteName)
	
	if doc:		
		doc_str = json.dumps(doc, default=str) 

		#print ("NODYYYYYYYY")
		#print (doc)
		#print (doc_str)

		headers = {}
		api_url = f"https://192.168.200.19:7037/api/v2/Download/{typeFile}?documentName={doc_name}&tip_doc={typeDocSri}&sitename={siteName}"	
		#response = requests.post(api_url, json=doc_str, verify=False, stream=True, headers= headers)
		response = requests.post(api_url, data=doc_str, verify=False, stream=True, headers= headers)
		return response.text

	return ""

	#print(doc_name)
	#print(doc.customer_email_id)

	#print(doc.sri_validated)
	#print(doc.sri_validated_message)

	
	#print(doc_str)

	#json -> object
	# x = json.loads(doc, object_hook=lambda d: SimpleNamespace(**d))
	# print("get_doc")
	# print(x.name)
	
	#headers = { "Authorization" : "our_unique_secret_token" }
	# headers = {}

	# data = {
	# 	"id": 1001,
	# 	"name": "geek",
	# 	"passion": "coding",
	# }
	
	# api_url = f"https://192.168.204.66:7037/api/v2/Download/{typeFile}?documentName={doc_name}&tip_doc={typeDocSri}&sitename={siteName}"
	
	#response = requests.post(api_url, json=doc_str, verify=False, stream=True, headers= headers)
	# response = requests.post(api_url, data=doc_str, verify=False, stream=True, headers= headers)
	
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

	# return response.text

@frappe.whitelist()
def send_doc(doc, typeDocSri, doctype_erpnext, siteName):	
	
	doc_data = None

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

	#	SE OMITE ESTE PASO
	doc_object_build = json.loads(doc, object_hook=lambda d: SimpleNamespace(**d))
	print("DESDE OBJETO")
	print(doc_object_build.name)
	print(typeDocSri)
	#   ----------------

	level = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
	#time.sleep(5)
	level += '   RESPUESTA SRI   ' # + doc.name
	level += datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

	match typeDocSri:
		case "FAC":
			doc_data = build_doc_fac(doc_object_build.name)
			print ("")
		case "GRS":
			doc_data = build_doc_grs(doc_object_build.name)
		case "CRE":
			doc_data = build_doc_cre(doc_object_build.name)

	#Preparar documento enviarlo al servicio externo de autorización
	#---------------------------------------------------------------
	# Obtener configuracion desde los datos
	# - url_server_beebtech
	# , filters = { 'reference_name': doc_name }, fields='*'
	settings_ec = frappe.get_list(doctype='Regional Settings Ec', fields='*')
	#print(settings_ec)
	
	url_server_beebtech = '';

	if settings_ec:
		url_server_beebtech = settings_ec[0].url_server_beebtech
		#print(url_server_beebtech)

	#api_url = "http://localhost:3003/api/Download/xml/MAT-DT-2023-00065?tip_doc=GRS&sitename=hdc"
	
	is_simulation_mode = True
	
	if(is_simulation_mode):
		#Modo de simulación
		api_url = f"{url_server_beebtech}/Tool/Simulate"
	else:
		#Envío normal
		api_url = f"{url_server_beebtech}/sendmethod"
	
	#print(doc_data)

	if (doc_data):
		doc_str = json.dumps(doc_data, default=str)

		print ("NODYYYYYYYY")
		print (doc_data)
		print (doc_str)

		headers = {}
		#api_url = f"https://192.168.204.66:7037/api/v2/Download/{typeFile}?documentName={doc_name}&tip_doc={typeDocSri}&sitename={siteName}"	
		#response = requests.post(api_url, json=doc_str, verify=False, stream=True, headers= headers)
		
		if(is_simulation_mode):
			response = requests.post(api_url, verify=False, stream=True)
		else:
			response = requests.post(api_url, data=doc_str, verify=False, stream=True, headers= headers)

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

				#Se agrega un nuevo Xml Response para que se lance el evento y se envie el email
				xml_response_new = frappe.get_doc({
					'id': 1,
					'doctype': 'Xml Responses',
					'description': "[Description]", #f"{doc.name} Added",        
				})

				signature_object = frappe.get_last_doc('Sri Signature', filters = { 'tax_id': '091982695800111'})
				#signature_object = frappe.get_doc('Sri Signature','EXP-2024-00097')			

				xml_response_new.insert()
				frappe.db.commit()

				if(signature_object):
					print(signature_object)
					print(signature_object.p12)

					if(signature_object.p12):
						input_data = open('../' + signature_object.p12).read()						

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