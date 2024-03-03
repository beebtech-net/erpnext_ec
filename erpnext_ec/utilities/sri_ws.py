# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

#from erpnext_ec.erpnext_ec.doctype import xml_responses

from datetime import datetime, date, timedelta
import time
import frappe
from frappe import _
import erpnext
#from frappe.utils.pdf import get_pdf

import json
from types import SimpleNamespace
import requests
from erpnext_ec.utilities.encryption import *

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# from bson import json_util
# import json

import dicttoxml

import re
import base64
from dateutil import parser

from erpnext_ec.utilities.doc_builder_fac import build_doc_fac 
from erpnext_ec.utilities.doc_builder_grs import build_doc_grs
from erpnext_ec.utilities.doc_builder_cre import build_doc_cre

@frappe.whitelist()
def send_email(doc, typeDocSri, doctype_erpnext, siteName, email_to):	
	#var url = `${btApiServer}/api/Tool/AddToEmailQuote/${doc}?tip_doc=FAC&sitename=${sitenameVar}&email_to=${values.email_to}`;
	pass


@frappe.whitelist()
def get_info_doc(doc_name, typeDocSri, doctype_erpnext, siteName):
	#print(doc)
	#var url = `${btApiServer}/api/SriProcess/getresponses/${doc}?tip_doc=${tip_doc}&sitename=${sitenamePar}`;
	#xml_responses = frappe.get_list(doctype='Xml Responses', fields='*')
	info_doc = {}
	xml_responses = get_responses(doc_name, typeDocSri, doctype_erpnext, siteName)
	
	for xml_response_item in xml_responses:
		print(xml_response_item.xmldata)

	doc_json = get_doc_json(doc_name, typeDocSri, doctype_erpnext, siteName)
	info_doc['responses'] = xml_responses
	info_doc['doc_json'] = doc_json
	print(info_doc)
	return info_doc

@frappe.whitelist()
def get_responses(doc_name, typeDocSri, doctype_erpnext, siteName):
	#print(doc)
	#var url = `${btApiServer}/api/SriProcess/getresponses/${doc}?tip_doc=${tip_doc}&sitename=${sitenamePar}`;
	#xml_responses = frappe.get_list(doctype='Xml Responses', fields='*')
	xml_responses = frappe.get_all('Xml Responses', filters={'doc_ref': doc_name, 'tip_doc': typeDocSri }, fields=['*'], order_by='creation')
	print(xml_responses)
	return xml_responses

def get_api_url():
	settings_ec = frappe.get_list(doctype='Regional Settings Ec', fields='*')
	#print(settings_ec)
	
	url_server_beebtech = '';

	if settings_ec:
		url_server_beebtech = settings_ec[0].url_server_beebtech
		server_timeout = settings_ec[0].server_timeout
		if(server_timeout == 0):
			server_timeout = 10
		return url_server_beebtech, server_timeout
	
	raise ReferenceError("No se encontró configuración requerida 'Regional Settings Ec' url_server_beebtech")
	#raise TypeError("El objeto de tipo %s no es serializable JSON." % type(obj).__name__)
	#return ""


@frappe.whitelist()
def get_doc_json(doc_name, typeDocSri, typeFile, siteName):

	doc = None
	print(doc_name, typeDocSri, typeFile, siteName)

	#El parametro doc aquí es el nombre del documento
      
	match typeDocSri:
		case "FAC":
			doc = build_doc_fac(doc_name)
			print ("")
		case "GRS":
			doc = build_doc_grs(doc_name)
		case "CRE":
			doc = build_doc_cre(doc_name)
			print(doc)

	return doc


@frappe.whitelist()
def get_doc_blob(doc_name, typeDocSri, typeFile, siteName):

	print(doc_name, typeDocSri, typeFile, siteName)

	#El parametro doc aquí es el nombre del documento
      
	match typeDocSri:
		case "FAC":
			doc = build_doc_fac(doc_name)
			print ("")
		case "GRS":
			doc = build_doc_grs(doc_name)
		case "CRE":
			doc = build_doc_cre(doc_name)
			print(doc)
	
	if doc:		
		doc_str = json.dumps(doc, default=str) 

		headers = {}
		
		url_server_beebtech, server_timeout = get_api_url()
		
		print(url_server_beebtech)
		print(server_timeout)

		api_url = f"{url_server_beebtech}/Download/{typeFile}?documentName={doc_name}&tip_doc={typeDocSri}&sitename={siteName}"	
		
		response = requests.post(api_url, data=doc_str, verify=False, stream=True, headers= headers, timeout=server_timeout)
		response.raise_for_status()

		print(response.status_code)

		if (response.status_code == 200):
			frappe.local.response.filename = doc_name + "." + typeFile
			frappe.local.response.filecontent = response.content
			frappe.local.response.type = "download"
		else:
			print("Error pos!")
			raise SystemError("No se pudo descargar archivo." + doc_name)

	#return ""

@frappe.whitelist()
def get_doc(doc_name, typeDocSri, typeFile, siteName):

	print(doc_name, typeDocSri, typeFile, siteName)

	#El parametro doc aquí es el nombre del documento
      
	match typeDocSri:
		case "FAC":
			doc = build_doc_fac(doc_name)
			print ("")
		case "GRS":
			doc = build_doc_grs(doc_name)
		case "CRE":
			doc = build_doc_cre(doc_name)
			print(doc)
	
	if doc:		
		doc_str = json.dumps(doc, default=str) 

		#print ("NODYYYYYYYY")
		#print (doc)
		#print (doc_str)

		headers = {}
		
		url_server_beebtech, server_timeout = get_api_url()
		#url_server_beebtech = "https://192.168.200.9:7037/api/v2"
		print(url_server_beebtech)
		print(server_timeout)

		api_url = f"{url_server_beebtech}/Download/{typeFile}?documentName={doc_name}&tip_doc={typeDocSri}&sitename={siteName}"	
		#response = requests.post(api_url, json=doc_str, verify=False, stream=True, headers= headers)
		response = requests.post(api_url, data=doc_str, verify=False, stream=True, headers= headers, timeout=server_timeout)

		#print(response.headers['Content-Type'])
		#print(response.text)
		print(response)
		return response.text
		#frappe.local.response.filename = "nombre_del_archivo.pdf"
		#frappe.local.response.filecontent = response.content
		#frappe.local.response.type = "download"

	return ""


def handler(obj):
    
	if isinstance(obj, datetime):
		return obj.isoformat()
	elif isinstance(obj, date):
		return obj.isoformat()	
	elif isinstance(obj, timedelta):
		return obj.total_seconds()	
	elif isinstance(obj, bytes):
		print('ENTRO EN EL BYTES!!!!')
		return base64.b64encode(obj).decode('utf-8')
	
	raise TypeError("El objeto de tipo %s no es serializable JSON." % type(obj).__name__)

def validate_doc(doc, typeDocSri, doctype_erpnext, siteName):
	#match typeDocSri:
	#	case "FAC":
	#		doc.
	#	case "GRS":
	#		
	#	case "CRE":

	print ('---------------')
	print ('validacion')
	print (doc)
	print(doc.customer_tax_id)
	print(doc.RazonSocial)
	print(doc.tipoIdentificacionComprador)
	
	raise ValueError("Error de validación %s" % type(doc).__name__)

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
	
	#print(doc.company)

	#	SE OMITE ESTE PASO
	doc_object_build = json.loads(doc, object_hook=lambda d: SimpleNamespace(**d))
	#print("DESDE OBJETO")
	#print(doc_object_build.name)
	#print(typeDocSri)
	#   ----------------

	level = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
	#time.sleep(5)
	level += '   RESPUESTA SRI   ' # + doc.name
	level += datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

	#Si se asigna correctamente el secuencial
	if setSecuencial(doc_object_build, typeDocSri):
		#Hacer algo?
		pass
	else:
		raise ReferenceError("No se encontró configuración requerida 'Sri Sequence' para la empresa "+ doc_object_build.company)
		
	match typeDocSri:
		case "FAC":
			
			doc_data = build_doc_fac(doc_object_build.name)
			
			print('-----------------------')
			print(doc_data.secuencial)
			print('-----------------------')
		case "GRS":
			doc_data = build_doc_grs(doc_object_build.name)
			
		case "CRE":
			doc_data = build_doc_cre(doc_object_build.name)
	
	#TODO: Validacion de los datos previo al envío al SRI
	#validate_doc(doc_data, typeDocSri, doctype_erpnext, siteName)

	#Preparar documento enviarlo al servicio externo de autorización
	#---------------------------------------------------------------
	url_server_beebtech, server_timeout = get_api_url()

	#print(url_server_beebtech)

	is_simulation_mode = False
	
	if(is_simulation_mode):
		#Modo de simulación
		api_url = f"{url_server_beebtech}/Tool/Simulate"
	else:
		#Envío normal
		#https://localhost:7037/api/v2/SriProcess/sendmethod
		api_url = f"{url_server_beebtech}/SriProcess/sendmethod?tip_doc={typeDocSri}&sitename={siteName}" 
	
	#print(doc_data)
	#print(api_url)

	if (doc_data):
		#signatureP12 = get_signature(doc_data.tax_id)
		#print(type(signatureP12))
		#doc_data.signatureP12 = signatureP12
		#data_str = b"Este es un mensaje de prueba"
		#signatureP12 = base64.b64encode(data_str).decode('utf-8')
		#doc_data.signatureP12 = signatureP12

		#doc_str = json.dumps(doc_data, default=handler)
		doc_str = json.dumps(doc_data, default=str)
		#doc_data = json.loads(doc_str)
		#doc_data.signatureP12 = signatureP12

		#print ("NODYYYYYYYY")
		#print (doc_data)
		#print (doc_str)

		headers = {}
		#api_url = f"https://192.168.204.66:7037/api/v2/Download/{typeFile}?documentName={doc_name}&tip_doc={typeDocSri}&sitename={siteName}"	
		#response = requests.post(api_url, json=doc_str, verify=False, stream=True, headers= headers)

		if(is_simulation_mode):
			response = requests.post(api_url, verify=False, stream=True, timeout=server_timeout)
		else:
			response = requests.post(api_url, data=doc_str, verify=False, stream=True, headers= headers, timeout=server_timeout)
			#response = requests.post(api_url, json=doc_data, verify=False, stream=True, headers= headers)

		#for k,v in r.raw.headers.items(): print(f"{k}: {v}")
		#print(r.text)		
		#print(response.text);
		#print(response.status_code);
			
		print(response)
		print(response.text)

		print('Numero de respuesta')		
		
		response_json = json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))

		#print(json.loads(response.text))
		#TODO: Conversión del XML para guardar en la base de datos es correcta, pero no agrega la declaracion:
		# <?xml version="1.0" encoding="UTF-8" standalone="yes"?>

		response_xml_data = dicttoxml.dicttoxml(json.loads(response.text)['data'], encoding="UTF-8", attr_type=False, root=False, xml_declaration=True)
		response_xml_data_string = response_xml_data
		# Imprimir el XML resultante
		#response_xml_data_string = response_xml_data.decode() #no funciona 
		#print(response_xml_data_string)

		print(response.status_code)
		print(response.ok)

		response_ok = response.ok

		if(response.status_code == 400):
			registerResponse(doc_data, typeDocSri, doctype_erpnext, response_json, response_xml_data_string)
			if(response_json.data.numeroComprobantes is not None and int(response_json.data.numeroComprobantes) > 0):
				if( 'ya estaba autorizada' in response_json.error):
					print ("correcto ya registrado previamente")
					#Se simula que el proceso fue correcto para que los datos sean actualizados
					response.status_code = 200
					response_ok = True

		if(response.status_code == 200):
			
			#registerResponse(doc_data, typeDocSri, doctype_erpnext, response_json, response.text)
			registerResponse(doc_data, typeDocSri, doctype_erpnext, response_json, response_xml_data_string)

			#evaluar estado de respuesta SRI
			if(response_ok and int(response_json.data.numeroComprobantes) > 0):
				print ("correcto")

				print(response_json)

				#proceder a actualizar datos del registro	
				print(response_json.data.claveAccesoConsultada)
				print(response_json.data.numeroComprobantes)
				print(response_json.data.autorizaciones.autorizacion[0].estado)
				print(response_json.data.autorizaciones.autorizacion[0].numeroAutorizacion)
				print(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)
				print(response_json.data.autorizaciones.autorizacion[0].ambiente)

				#Se agrega un nuevo Xml Response para que se lance el evento y se envie el email
				# xml_response_new = frappe.get_doc({
				# 	'id': 1,
				# 	'doctype': 'Xml Responses',
				# 	'description': "[Description]", #f"{doc.name} Added",        
				# })							

				# xml_response_new.insert()
				# frappe.db.commit()

				if(response_json.data.autorizaciones.autorizacion[0].estado == "AUTORIZADO"):
					updateStatusDocument(doc_object_build, typeDocSri, response_json)

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

def setSecuencial(doc, typeDocSri):
	
	company_object = frappe.get_last_doc('Company', filters = { 'name': doc.company  })
	#company_object.name
	#company_object.sri_active_environment
	
	match typeDocSri:
		case "FAC":
			
			#print(doc)
			document_object = frappe.get_last_doc('Sales Invoice', filters = { 'name': doc.name})
			if(document_object):
				if(document_object.secuencial > 0):
					print("Secuencial ya asignado!")
					print(document_object.secuencial)
					return True

		case "GRS":
			
			#print(doc)
			document_object = frappe.get_last_doc('Delivery Note', filters = { 'name': doc.name})
			if(document_object):
				if(document_object.secuencial > 0):
					print("Secuencial ya asignado!")
					print(document_object.secuencial)
					return True

		case "CRE":
			
			#print(doc)
			document_object = frappe.get_last_doc('Purchase Withholding Sri Ec', filters = { 'name': doc.name})
			if(document_object):
				if(document_object.secuencial > 0):
					print("Secuencial ya asignado!")
					print(document_object.secuencial)
					return True

	#PROCESO GENERAL -----
	#doc.ambiente ---- aun no asignado   --- probablemente desde company
	#environment_object = frappe.get_last_doc('Sri Environment', filters = { 'id': 1  })
	#print(environment_object.name)
	#print(environment_object.id)

	print("--------------------------")
	nuevo_secuencial = 0

	#TODO: Agregar filtro por empresa, no fue considerado al inicio, se requerirá cambios en el modelo
	#TODO: Falta automatizar el filtro, por ahora se puso id = 1
	#sequence_object = frappe.get_last_doc('Sri Sequence', filters = { 'id': 1, 'sri_environment_lnk': environment_object.name, 'sri_type_doc_lnk': typeDocSri })
	
	#sequence_object = frappe.get_last_doc('Sri Sequence', filters = { 'company_id': company_object.name, 'sri_environment_lnk': company_object.sri_active_environment, 'sri_type_doc_lnk': typeDocSri })
	sequence_object = frappe.get_list('Sri Sequence', fields = ['*'], filters = { 'company_id': company_object.name, 'sri_environment_lnk': company_object.sri_active_environment, 'sri_type_doc_lnk': typeDocSri })
	#sequence_object = frappe.get_list('Sri Sequence', filters = { 'reference_name': doc_name })

	#print(sequence_object[0])
	
	if (sequence_object):
		print(sequence_object[0].value)
		nuevo_secuencial = sequence_object[0].value
		nuevo_secuencial += 1
		print(nuevo_secuencial)
		#Se asigna al documento
		document_object.db_set('secuencial', nuevo_secuencial)
		#Se asigna a la tabla de secuenciales

		#Actualizar dato de secuencia
		doc_sequence_object = frappe.get_last_doc('Sri Sequence', filters = { 'id': sequence_object[0].id })
		doc_sequence_object.db_set('value', nuevo_secuencial)
		return True
	else:
		return False


def registerResponse(doc, typeDocSri, doctype_erpnext, response_json, response_json_text):
	#TODO: El XML se guarda de forma incorrecta, pero al parecer es un comportamiento normal
	# del frappe, hay que verificar.
	xml_response_new = frappe.get_doc({
					'doctype': 'Xml Responses',
					'doc_ref': doc.name,
					#'xmldata': response_json.data.autorizaciones.autorizacion[0].comprobante,
					'xmldata': response_json_text,
					'sri_status': response_json.data.autorizaciones.autorizacion[0].estado,
					'tip_doc': typeDocSri,
					'doc_type': doctype_erpnext
				})

	xml_response_new.insert()
	frappe.db.commit()

def updateStatusDocument(doc, typeDocSri, response_json):
	match typeDocSri:
		case "FAC":
			document_object = frappe.get_last_doc('Sales Invoice', filters = { 'name': doc.name })
			if(document_object):
				document_object.db_set('numeroautorizacion', response_json.data.autorizaciones.autorizacion[0].numeroAutorizacion)
				document_object.db_set('sri_estado', 200)
				document_object.db_set('sri_response', response_json.data.autorizaciones.autorizacion[0].estado)
				#fechaAutorizacion = parser.parse(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)

				fecha_con_zona = datetime.fromisoformat(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)
				# Eliminar la zona horaria
				fechaAutorizacion = fecha_con_zona.replace(tzinfo=None)

				#print(fechaAutorizacion)
				#print(type(fechaAutorizacion))
				#print(datetime.now())
				#print(type(datetime.now()))

				document_object.db_set('fechaautorizacion', fechaAutorizacion)
				#document_object.db_set('fechaautorizacion', datetime.now())
				
				#NO ES NECESARIO EJECUTAR SAVE
				#document_object.save(
				#	ignore_permissions=True, # ignore write permissions during insert
				#	ignore_version=True # do not create a version record
				#)
	
		case "GRS":
			
			print(response_json)

			document_object = frappe.get_last_doc('Delivery Note', filters = { 'name': doc.name })
			if(document_object):				
				document_object.db_set('numeroautorizacion', response_json.data.autorizaciones.autorizacion[0].numeroAutorizacion)
				document_object.db_set('sri_estado', 200)
				document_object.db_set('sri_response', response_json.data.autorizaciones.autorizacion[0].estado)
				#fechaAutorizacion = parser.parse(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)
				fecha_con_zona = datetime.fromisoformat(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)
				# Eliminar la zona horaria
				fechaAutorizacion = fecha_con_zona.replace(tzinfo=None)

				#print(fechaAutorizacion)
				#print(type(fechaAutorizacion))
				#print(datetime.now())
				#print(type(datetime.now()))

				document_object.db_set('fechaautorizacion', fechaAutorizacion)

		#case "CRE":
			#doc_data = build_doc_cre(doc_object_build.name)