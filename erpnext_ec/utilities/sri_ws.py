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
#from erpnext_ec.utilities.encryption import *
from erpnext_ec.utilities.signature_tool import *
from erpnext_ec.utilities.xml_builder import *
from erpnext_ec.utilities.xades_tool_v2 import *

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# from bson import json_util
# import json

import dicttoxml
import xmltodict

import re
import base64
from dateutil import parser

from erpnext_ec.utilities.doc_builder_fac import build_doc_fac 
from erpnext_ec.utilities.doc_builder_grs import build_doc_grs
from erpnext_ec.utilities.doc_builder_cre import build_doc_cre

from erpnext_ec.utilities.email_tool import sendmail

from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

from suds import WebFault
from suds.client import Client

@frappe.whitelist()
def test_signature(signature_doc):
	#print ("----")
	#print(signature_doc)
	#Este metodo aun utiliza el api
	doc_data = build_doc_fac('ACC-SINV-2024-00001')
	#archivo XML de prueba
	full_path_doc = '/opt/bench/frappe-bench/sites/principal/private/files/ACC-SINV-2024-00001.xml'
	file = open(full_path_doc, "r")
	doc_text = file.read()
	file.close()
	#print(doc_text)

	#doc_text = get_doc('ACC-SINV-2024-00001', 'FAC', 'xml', 'principal')
	signed_xml = SriXmlData.sign_xml(SriXmlData, doc_text, doc_data, signature_doc)
	#print(signed_xml)
	return signed_xml

@frappe.whitelist()
def verify_signature(signature_doc):	
	
	#doc_text = get_doc('ACC-SINV-2024-00001', 'FAC', 'xml', 'principal')
	private_key, p12 = SriXmlData.get_sri_signature(SriXmlData, signature_doc)
	print(private_key)
	print(p12)

	#propietario = p12.subject.rfc4514_string() #certificado_decodificado.subject.rfc4514_string()
	#fecha_emision = p12.not_valid_before #certificado_decodificado.not_valid_before
	#fecha_expiracion = p12.not_valid_after

	#print("Propietario:", propietario)
	#print("Fecha de emisión:", fecha_emision)
	#print("Fecha de expiración:", fecha_expiracion)

	if(private_key is None and p12 is None):
		return_object = {
			"tax_id": "",
			"issuer": "",
			"thumbprint":"",
			"subject": "",
			"not_valid_before": "",
			"not_valid_after":"",
			"status": "fail"
		}
		return return_object 

	tax_id = ""
	x509_to_review = p12
	for exten in x509_to_review.extensions:		
		#print(exten)
		#break
		if(exten.value.oid.dotted_string=="1.3.6.1.4.1.37746.3.11"):			
			#print(exten.value.value.decode())
			#print(exten.value.oid)
			tax_id = exten.value.value.decode()
			break
            #if exten.oid._name == "keyUsage" and exten.value.digital_signature:
            #    is_digital_signature = True
            #    break
	
	#print(p12.issuer.rfc4514_string())
	#print(p12.issuer.human_friendly)

	issuerName = p12.issuer.rfc4514_string()
	
	return_object = {
		"tax_id": tax_id,
		"issuer": issuerName,
		"thumbprint":"",
		"subject": p12.subject.rfc4514_string(),
		"not_valid_before": p12.not_valid_before,
		"not_valid_after":p12.not_valid_after,
		"status": "success"
	}
	return return_object


@frappe.whitelist()
def add_email_quote(doc_name, recipients, msg, title, typeDocSri, doctype_erpnext, use_doc_email):

	doc_data = []
	template_name = ''	#email body template
	template = ''
	print_format_name = ''
	email_subject = ''

	#Python 3.6 incompatible
	# match typeDocSri:
	# 	case "FAC":
	# 		doc_data = build_doc_fac(doc_name)
	# 		template_name = 'Factura SRI Body'
	# 		print_format_name = 'Factura SRI'
	# 	case "GRS":
	# 		doc_data = build_doc_grs(doc_name)
	# 	case "CRE":
	# 		doc_data = build_doc_cre(doc_name)

	#Python 3.6 compatible
	if typeDocSri == "FAC":
			doc_data = build_doc_fac(doc_name)
			template_name = 'Factura SRI Body'
			print_format_name = 'Factura SRI'
			email_subject = f'Factura Electrónica {doc_data.estab }-{doc_data.ptoemi}-{doc_data.secuencial:09d}'			
	elif typeDocSri == "GRS":
			doc_data = build_doc_grs(doc_name)
			template_name = 'Guia Remision Sri Body'
			email_subject = f'Guía de Remisión {doc_data.estab }-{doc_data.ptoemi}-{doc_data.secuencial:09d}'
	elif typeDocSri == "CRE":
			doc_data = build_doc_cre(doc_name)
			email_subject = f'Comprobante de Retención {doc_data.estab }-{doc_data.ptoemi}-{doc_data.secuencial:09d}'
	
	print("---------ENVIANDO")
	#print(doc_data)

	templates = frappe.get_list('Email Template', fields = ['*'], filters = { 'name': template_name })

	if(templates):
		template = templates[0].response_html

	#print(template)

	msg_template = frappe.render_template(template, { "doc": doc_data }) 
	
	print(msg_template)

	#build attachments
	xml_responses = frappe.get_list('Xml Responses', fields = ['*'], filters = { 'doc_ref': doc_name, 'tip_doc': typeDocSri, 'sri_status': 'AUTORIZADO' })

	attach_file_name = doc_data.estab + doc_data.ptoemi + f'{doc_data.secuencial:09d}'

	attachments = []
	#Attach Zip with XMl
	if(xml_responses):
		
		attach_file_name_zip = attach_file_name + '.zip' #doc_data.numeroautorizacion + '.zip'
		attach_file_name_xml = attach_file_name + '.xml' #doc_data.numeroautorizacion + '.xml'
		
		xml_data = xml_responses[0].xmldata
		import io
		import zipfile
		#file_like_object = io.BytesIO(b"{xml_data}")
		archive = io.BytesIO()
		with zipfile.ZipFile(archive, 'w') as zip_archive:
			zip_archive.writestr( attach_file_name_xml, xml_data)
			#with zip_archive.open('authorized.xml', 'w') as file1:
				#file1.write(file_like_object)
				#file1.write(b"{xml_data}")
				#print(archive.getvalue())
		
		attachments.append({"fname": attach_file_name_zip, "fcontent": archive.getvalue()})
	
	#Attach PDF
	attach_file_name_pdf = attach_file_name
	doc_data.doctype = doctype_erpnext
	#print(doc_data)

	#pdf_attachment = [frappe.attach_print(doc_data.doctype, doc_data.name, file_name=attach_file_name_pdf, print_format = print_format_name, print_letterhead=True)]
	pdf_attachment = [frappe.attach_print(doc_data.doctype, doc_data.name, file_name=attach_file_name_pdf, print_format = print_format_name)]
	
	if(pdf_attachment):
		attachments.append(pdf_attachment[0])

	#my_attachments = [frappe.attach_print(self.doctype, self.name, file_name=self.name)]

	print('LISTO PARA ENVIAR')
	print(recipients)
	print(use_doc_email)

	if((recipients == "" or not recipients) and use_doc_email == "1"):
		print('Se usará email de documento')
		recipients = doc_data.customer_email_id

	print("recipients final:")
	print(recipients)
	#var url = `${btApiServer}/api/Tool/AddToEmailQuote/${doc}?tip_doc=FAC&sitename=${sitenameVar}&email_to=${values.email_to}`;
	sendmail(doc_data, recipients, email_subject, msg_template, attachments)	        
	pass

@frappe.whitelist()
def download_pdf(doc_name, typeDocSri, typeFile, siteName):

	doc_data = []
	template_name = ''	#email body template
	template = ''
	print_format_name = ''
	email_subject = ''
	doctype_erpnext = ''

	#Python 3.6 compatible
	if typeDocSri == "FAC":
			doc_data = build_doc_fac(doc_name)
			doctype_erpnext = 'Sales Invoice'
			print_format_name = 'Factura SRI'
			
	elif typeDocSri == "GRS":
			doc_data = build_doc_grs(doc_name)
			doctype_erpnext = 'Delivery Note'
			print_format_name = 'Guia de Remision SRI'
			
	elif typeDocSri == "CRE":
			doc_data = build_doc_cre(doc_name)			
			doctype_erpnext = 'Purchase Withholding Sri Ec'
			print_format_name = 'Retencion SRI'
			
	templates = frappe.get_list('Email Template', fields = ['*'], filters = { 'name': template_name })

	if(templates):
		template = templates[0].response_html

	#print(template)
	
	attach_file_name = doc_data.estab + doc_data.ptoemi + f'{doc_data.secuencial:09d}'
	
	attach_file_name_pdf = attach_file_name
	doc_data.doctype = doctype_erpnext
	#print(doc_data)

	pdf_attachment = [frappe.attach_print(doc_data.doctype, doc_data.name, file_name=attach_file_name_pdf, print_format = print_format_name)]
	
	typeFile = 'pdf'
	#print(pdf_attachment[0])
	if(pdf_attachment):		
  	    #print(type(pdf_attachment[0]))
		frappe.local.response.filename = doc_name + "." + typeFile
		frappe.local.response.filecontent = pdf_attachment[0]['fcontent']
		frappe.local.response.type = "download"


@frappe.whitelist()
def get_info_doc(doc_name, typeDocSri, doctype_erpnext, siteName):
	#print(doc)
	#var url = `${btApiServer}/api/SriProcess/getresponses/${doc}?tip_doc=${tip_doc}&sitename=${sitenamePar}`;
	#xml_responses = frappe.get_list(doctype='Xml Responses', fields='*')
	info_doc = {}
	xml_responses = get_responses(doc_name, typeDocSri, doctype_erpnext, siteName)
	
	#for xml_response_item in xml_responses:
	#	print(xml_response_item.xmldata)

	doc_json = get_doc_json(doc_name, typeDocSri, doctype_erpnext, siteName)
	info_doc['responses'] = xml_responses
	info_doc['doc_json'] = doc_json
	#print(info_doc)
	
	#print(doc_json.estab + "-" + doc_json.ptoemi + "-" + '{:09d}'.format(doc_json.secuencial) )

	return info_doc

@frappe.whitelist()
def get_responses(doc_name, typeDocSri, doctype_erpnext, siteName):
	#print(doc)
	#var url = `${btApiServer}/api/SriProcess/getresponses/${doc}?tip_doc=${tip_doc}&sitename=${sitenamePar}`;
	#xml_responses = frappe.get_list(doctype='Xml Responses', fields='*')
	xml_responses = frappe.get_all('Xml Responses', filters={'doc_ref': doc_name, 'tip_doc': typeDocSri }, fields=['*'], order_by='creation')
	#print(xml_responses)
	return xml_responses

def get_api_url():
	settings_ec = frappe.get_list(doctype='Regional Settings Ec', fields='*')
	#print(settings_ec)
	
	url_server_beebtech = '';

	if settings_ec:
		
		url_server_beebtech = settings_ec[0].url_server_beebtech
		server_timeout = settings_ec[0].server_timeout

		if(settings_ec[0].use_external_service):
			pass
		
		if(server_timeout == 0):
			server_timeout = 10
		return url_server_beebtech, server_timeout
	
	raise ReferenceError("No se encontró configuración requerida 'Regional Settings Ec' url_server_beebtech")
	#raise TypeError("El objeto de tipo %s no es serializable JSON." % type(obj).__name__)
	#return ""


@frappe.whitelist()
def get_doc_json(doc_name, typeDocSri, typeFile, siteName):

	doc = None
	#print(doc_name, typeDocSri, typeFile, siteName)

	#El parametro doc aquí es el nombre del documento
    
	#Python 3.6 incompatible
	# match typeDocSri:
	# 	case "FAC":
	# 		doc = build_doc_fac(doc_name)
	# 		#print ("")
	# 	case "GRS":
	# 		doc = build_doc_grs(doc_name)
	# 	case "CRE":
	# 		doc = build_doc_cre(doc_name)
	# 		#print(doc)
	
	#Python 3.6 compatible	
	if typeDocSri == "FAC":
			doc = build_doc_fac(doc_name)
			#print ("")
	elif typeDocSri == "GRS":
			doc = build_doc_grs(doc_name)
	elif typeDocSri == "CRE":
			doc = build_doc_cre(doc_name)
			#print(doc)	

	return doc


@frappe.whitelist()
def get_doc_blob(doc_name, typeDocSri, typeFile, siteName):

	print(doc_name, typeDocSri, typeFile, siteName)

	#El parametro doc aquí es el nombre del documento
      
	if typeDocSri == "FAC":
			doc = build_doc_fac(doc_name)
			print ("")
	elif typeDocSri == "GRS":
			doc = build_doc_grs(doc_name)
	elif typeDocSri == "CRE":
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
			#test signature
			#response.content
			
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
      
	if typeDocSri == "FAC":
			doc = build_doc_fac(doc_name)
			print ("")
	elif typeDocSri == "GRS":
			doc = build_doc_grs(doc_name)
	elif typeDocSri == "CRE":
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
def send_doc_external(doc, typeDocSri, doctype_erpnext, siteName):	
	
	doc_data = None

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
	#if setSecuencial(doc_object_build, typeDocSri):
		#Hacer algo?
	#	pass
	#else:
	#	raise ReferenceError("No se encontró configuración requerida 'Sri Sequence' para la empresa "+ doc_object_build.company)
		
	if typeDocSri == "FAC":
			
			doc_data = build_doc_fac(doc_object_build.name)
			
			#print('-----------------------')
			#print(doc_data.secuencial)
			#print('-----------------------')
	elif typeDocSri == "GRS":
			doc_data = build_doc_grs(doc_object_build.name)
			
	elif typeDocSri == "CRE":
			doc_data = build_doc_cre(doc_object_build.name)
	
	#TODO: Validacion de los datos previo al envío al SRI
	#validate_doc(doc_data, typeDocSri, doctype_erpnext, siteName)

	#Preparar documento enviarlo al servicio externo de autorización
	#---------------------------------------------------------------
	url_server_beebtech, server_timeout = get_api_url()

	#print(url_server_beebtech)
	
	#Envío normal
	#https://localhost:7037/api/v2/SriProcess/sendmethod
	api_url = f"{url_server_beebtech}/SriProcess/sendmethod?tip_doc={typeDocSri}&sitename={siteName}" 
	
	#print(doc_data)
	#print(api_url)

	if (doc_data):
		
		doc_str = json.dumps(doc_data, default=str)		

		headers = {}
		#api_url = f"https://192.168.204.66:7037/api/v2/Download/{typeFile}?documentName={doc_name}&tip_doc={typeDocSri}&sitename={siteName}"	
		#response = requests.post(api_url, json=doc_str, verify=False, stream=True, headers= headers)
	
		response = requests.post(api_url, data=doc_str, verify=False, stream=True, headers= headers, timeout=server_timeout)
			#response = requests.post(api_url, json=doc_data, verify=False, stream=True, headers= headers)

		#for k,v in r.raw.headers.items(): print(f"{k}: {v}")
		#print(r.text)		
		#print(response.text);
		#print(response.status_code);
			
		#print(response)
		#print(response.text)

		print('Numero de respuesta')
		
		#print(response.text)

		response_json = json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))		
		response_xml_data = dicttoxml.dicttoxml(json.loads(response.text)['data'], encoding="UTF-8", attr_type=False, root=False, xml_declaration=True)
		response_xml_data_string = response_xml_data
		#print(response.status_code)
		#print(response.ok)
		response_ok = response.ok
		
		if(response.status_code == 400):
			registerResponse(doc_data, typeDocSri, doctype_erpnext, response_json, response_xml_data_string)
			if(response_json.data.numeroComprobantes is not None and int(response_json.data.numeroComprobantes) > 0):
				if( not response_json.error is None and  'ya estaba autorizada' in response_json.error):
					print ("correcto ya registrado previamente")					
					response.status_code = 200
					response_ok = True

		if(response.status_code == 200):		
			registerResponse(doc_data, typeDocSri, doctype_erpnext, response_json, response_xml_data_string)

		if(response_ok and int(response_json.data.numeroComprobantes) > 0):
			print ("correcto")
			print(response_json)
			print(response_json.data.claveAccesoConsultada)
			print(response_json.data.numeroComprobantes)
			print(response_json.data.autorizaciones.autorizacion[0].estado)
			print(response_json.data.autorizaciones.autorizacion[0].numeroAutorizacion)
			print(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)
			print(response_json.data.autorizaciones.autorizacion[0].ambiente)
			if(response_json.data.autorizaciones.autorizacion[0].estado == "AUTORIZADO"):					
				updateStatusDocument(doc_data, typeDocSri, response_json)
		
		#print(response_json.data)
		
		return response.text
	
		#api_url = "https://jsonplaceholder.typicode.com/todos/10"
		#response = requests.get(api_url)
		
		#print(response.json());

		#{'userId': 1, 'id': 10, 'title': 'illo est ... aut', 'completed': True}

		#todo = {"userId": 1, "title": "Wash car", "completed": True}
		#response = requests.put(api_url, json=todo)
		#print(response.json())
		#{'userId': 1, 'title': 'Wash car', 'completed': True, 'id': 10}

		#frappe.msgprint(f"{xml_response_new.id} has been created.")
		

def validaComprobanteSuds(xml_string):
	api_url = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
	
	wsClient = Client(api_url)

	responseXml = wsClient.service.validarComprobante(xml=xml_string)
	return responseXml

def validaComprobante(sri_environment, base64_string, server_timeout):	
	#Ambiente pruebas por defecto
	api_url = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"

	if (sri_environment.service_url_recept != api_url):
		api_url = sri_environment.service_url_recept

	print(api_url)

	body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ec="http://ec.gob.sri.ws.recepcion">
	<soapenv:Header/>
<soapenv:Body>
	<ec:validarComprobante>
		<xml><![CDATA[{}]]></xml>
	</ec:validarComprobante>
</soapenv:Body>
</soapenv:Envelope>""".format(base64_string)

	print(body)

	headers = {
		"Content-Type": "text/xml"
	}
	
	response = requests.post(api_url, data=body, verify=False, stream=True, headers= headers, timeout=server_timeout)

	#tree = ET.ElementTree(ET.fromstring(response.text))	
	#print(tree.find('RespuestaRecepcionComprobante').find('estado'))
	
	return response

def autorizacionComprobante(sri_environment, claveAccesoComprobante, server_timeout):
	#Ambiente pruebas por defecto
	api_url = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl"

	if (sri_environment.service_url_authorize != api_url):
		api_url = sri_environment.service_url_authorize

	print(api_url)
	body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ec="http://ec.gob.sri.ws.autorizacion">
   <soapenv:Header/>
   <soapenv:Body>
      <ec:autorizacionComprobante>
         <claveAccesoComprobante>{}</claveAccesoComprobante>
      </ec:autorizacionComprobante>
   </soapenv:Body>
</soapenv:Envelope>""".format(claveAccesoComprobante)

	headers = {
		"Content-Type": "text/xml"
	}
	
	response = requests.post(api_url, data=body, verify=False, stream=True, headers= headers, timeout=server_timeout)
	return response

def processAuthorization(doc_data, 
						 typeDocSri, 
						 doctype_erpnext, 
						 sri_environment, 
						 claveAccesoComprobante, 
						 server_timeout, 
						 response_xml_data_string, 
						 message_identificador,
						 message_text):

	response_auto = autorizacionComprobante(sri_environment, claveAccesoComprobante, server_timeout)

	#print(response_auto.text)
	
	response_xml_data_string = response_auto.text

	response_json_auto = xmltodict.parse(response_auto.text)
	#print(response_json_auto)
	response_json_auto_comprobantes = response_json_auto['soap:Envelope']['soap:Body']['ns2:autorizacionComprobanteResponse']['RespuestaAutorizacionComprobante']
	response_json_auto_final = response_json_auto['soap:Envelope']['soap:Body']['ns2:autorizacionComprobanteResponse']['RespuestaAutorizacionComprobante']	

	# Imprimir el XML resultante		
	#print(response_xml_data_string)

	response_ok = response_auto.ok

	if(response_auto.status_code == 400):
		registerResponse_native(doc_data, typeDocSri, doctype_erpnext, response_json_auto_comprobantes, response_xml_data_string)
		if(response_json_auto_comprobantes.numeroComprobantes is not None and int(response_json_auto_comprobantes.numeroComprobantes) > 0):
			#if( not response_json_auto_comprobantes.error is None and  'ya estaba autorizada' in response_json_auto_comprobantes.error):
			
			print ("correcto ya registrado previamente")
			#Se simula que el proceso fue correcto para que los datos sean actualizados
			response_auto.status_code = 200
			response_ok = True

	if(response_auto.status_code == 200):
		
		#registerResponse(doc_data, typeDocSri, doctype_erpnext, response_json, response.text)
		registerResponse_native(doc_data, typeDocSri, doctype_erpnext, response_json_auto_comprobantes, response_xml_data_string)

		#evaluar estado de respuesta SRI
		if(response_ok and int(response_json_auto_comprobantes['numeroComprobantes']) > 0):
			print ("correcto")

			print(response_json_auto_comprobantes)

			#proceder a actualizar datos del registro	
			print(response_json_auto_comprobantes['claveAccesoConsultada'])
			print(response_json_auto_comprobantes['numeroComprobantes'])
			print(response_json_auto_comprobantes['autorizaciones']['autorizacion']['estado'])
			#print(response_json_auto_comprobantes['claveAccesoConsultada'])
			print(response_json_auto_comprobantes['autorizaciones']['autorizacion']['fechaAutorizacion'])
			print(response_json_auto_comprobantes['autorizaciones']['autorizacion']['ambiente'])

			if(response_json_auto_comprobantes['autorizaciones']['autorizacion']['estado'] == "AUTORIZADO"):
				#updateStatusDocument(doc_object_build, typeDocSri, response_json)
				updateStatusDocument_native(doc_data, typeDocSri, response_json_auto_comprobantes)
	
	response_json_auto_final['ok'] = True
	if(message_identificador == '43' or message_identificador == '65'):		
		#if(response_json_auto_comprobantes.ok and int(response_json_auto_comprobantes['numeroComprobantes']) > 0):
		if(int(response_json_auto_comprobantes['numeroComprobantes']) > 0):
			if(response_json_auto_comprobantes['autorizaciones']['autorizacion']['estado'] == 'AUTORIZADO'):
				
				docIdSri = doc_data.estab + "-" + doc_data.ptoemi + "-" + str(doc_data.secuencial)

				custom_info = f"La factura {docIdSri} ya estaba autorizada, {claveAccesoComprobante}."
				response_json_auto_final['custom_info'] = custom_info
				response_json_auto_final['ok'] = False
		else:
			custom_info = f"Error {message_identificador} {message_text}, {doc_data.name}. No ha sido emitida previamente {claveAccesoComprobante}."
			response_json_auto_final['custom_info'] = custom_info
			response_json_auto_final['ok'] = False

	return response_json_auto_final

def BuildSimulationResponse():
	
	response_json_auto = {
		"claveAccesoConsultada": "1111122222333334444455555666667777788888999990000",
		"numeroComprobantes": "1",
		"autorizaciones": {
			"autorizacion": [
				{
					"estado": "AUTORIZADO",
					"numeroAutorizacion": "1111122222333334444455555666667777788888999990000",
					"fechaAutorizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
					"ambiente": "PRODUCCIÓN",
					"comprobante": "<?xml version=\"1.0\" encoding=\"utf-8\"?><factura xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" id=\"comprobante\" version=\"1.0.0\"><infoTributaria><ambiente>2</ambiente><tipoEmision>1</tipoEmision><razonSocial>RONALD STALIN CHONILLO VILLON</razonSocial><nombreComercial>RONALD STALIN CHONILLO VILLON</nombreComercial><ruc>0919826958001</ruc><claveAcceso>2802202301091982695800120010020000000321234567811</claveAcceso><codDoc>01</codDoc><estab>001</estab><ptoEmi>002</ptoEmi><secuencial>000000032</secuencial><dirMatriz>GUAYAQUIL BOSQUES DE LA COSTA, MZ 190 V 22</dirMatriz><contribuyenteRimpe>CONTRIBUYENTE RÉGIMEN RIMPE</contribuyenteRimpe></infoTributaria></factura>",
					"mensajes": {
						"mensaje": []
					}
				}
			]
		},
		"error": None,
		"ok": True
	}
	
	return response_json_auto

@frappe.whitelist()
def send_doc_native(doc, typeDocSri, doctype_erpnext, siteName):

	doc_data = None

	#NO SE OMITE ESTE PASO PORQUE SE REQUIERE EL NOMBRE DEL DOCUMENTO
	doc_object_build = json.loads(doc, object_hook=lambda d: SimpleNamespace(**d))
		
	doc_data = get_doc_native(doc_object_build, doc_object_build.name, typeDocSri, doctype_erpnext, siteName)
	
	if (doc_data):
		company_object = frappe.get_last_doc('Company', filters = { 'name': doc_data.company  })

		if(company_object.use_simulation_mode):
			print('SE USARA MODO DE SIMULACION')
			return BuildSimulationResponse()

		sri_environment = frappe.get_last_doc('Sri Environment', filters = { 'id': doc_data.ambiente })

		if (sri_environment):

			print(sri_environment.name)
			print(sri_environment.id)
		
		regional_settings_ec = frappe.get_last_doc('Regional Settings Ec', filters = { 'name': company_object.regional_settings_ec })
		print(regional_settings_ec)
		print('regional_settings_ec.signature_tool')
		print(regional_settings_ec.signature_tool)
		if(regional_settings_ec):
			if regional_settings_ec.use_external_service:
				#Se utilizará el servicio externo
				return send_doc_external(doc, typeDocSri, doctype_erpnext, siteName)
			else:
				#Se utilizará el servicio interno
				return send_doc_internal(doc, typeDocSri, doctype_erpnext, siteName, regional_settings_ec)

@frappe.whitelist()
def send_doc_internal(doc, typeDocSri, doctype_erpnext, siteName, regional_settings_ec):

	doc_data = None

	#NO SE OMITE ESTE PASO PORQUE SE REQUIERE EL NOMBRE DEL DOCUMENTO
	doc_object_build = json.loads(doc, object_hook=lambda d: SimpleNamespace(**d))
	
	#TODO: Validacion de los datos previo al envío al SRI
	#validate_doc(doc_data, typeDocSri, doctype_erpnext, siteName)
	
	doc_data = get_doc_native(doc_object_build, doc_object_build.name, typeDocSri, doctype_erpnext, siteName)

	#Preparar documento enviarlo al servicio externo de autorización
	#---------------------------------------------------------------
	url_server_beebtech, server_timeout = get_api_url()

	#print(url_server_beebtech)
	
	#print(doc_data)
	#print(api_url)
	
	if (doc_data):
		company_object = frappe.get_last_doc('Company', filters = { 'name': doc_data.company  })

		if(company_object.use_simulation_mode):
			print('SE USARA MODO DE SIMULACION')
			return BuildSimulationResponse()

		sri_environment = frappe.get_last_doc('Sri Environment', filters = { 'id': doc_data.ambiente })
		print(sri_environment.name)
		print(sri_environment.id)
 
		#sri_signatures = frappe.get_all('Sri Signature', filters={"tax_id": doc_data.tax_id}, fields = ['*'])
		sri_signatures = frappe.get_all('Sri Signature', filters={"name": company_object.sri_signature}, fields = ['*'])

		if(sri_signatures):
			#signatureP12 = sri_signatures[0]
			signatureP12 = json.dumps(sri_signatures[0], default=str)

		#doc_str = json.dumps(doc_data, default=str)

		xml_string = build_xml_data(doc_data, doc_data.name, typeDocSri, siteName)

		print('regional_settings_ec.signature_tool')
		print(regional_settings_ec.signature_tool)

		#Se firma el documento con la aplicacion externa XadesSignerCmd
		if(regional_settings_ec.signature_tool == "XadesSignerCmd"):
			signed_xml = SriXmlData.sign_xml_cmd(SriXmlData, xml_string, sri_signatures[0])

		if(regional_settings_ec.signature_tool == "Python Native (With Fails)"):            
			#signed_xml = SriXmlData.sign_xml(SriXmlData, xml_string, doc_data, sri_signatures[0])
			#signed_xml = SriXmlData.sign_xml_xades(SriXmlData, xml_string, sri_signatures[0])			
			signed_xml =XadesToolV2.sign_xml(SriXmlData, xml_string, doc_data, sri_signatures[0])
	
		#print(xml_string)

		#signed_xml = build_xml_signed(xml_string, doc_data, signatureP12)
		#signed_xml = SriXmlData.sign_xml_old(SriXmlData, xml_string, signatureP12)  		

		print(signed_xml)
		#print(type(str(signed_xml)))
		xml_bytes = signed_xml.encode()

		base64_string = base64.b64encode(bytes(signed_xml,'utf-8')).decode('utf-8')
		
		response = validaComprobante(sri_environment, base64_string, server_timeout)

		print('Numero de respuesta')
		
		print(response)
		
		response_valida_json_auto = xmltodict.parse(response.text)
		
		print(response_valida_json_auto)

		#informacion_adicional = json_data['soap:Envelope']['soap:Body']['ns2:validarComprobanteResponse']['RespuestaRecepcionComprobante']['comprobantes']['comprobante']['mensajes']['mensaje']['informacionAdicional']
		#estado = json_data['soap:Envelope']['soap:Body']['ns2:validarComprobanteResponse']['RespuestaRecepcionComprobante']['estado']
		response_valida = response_valida_json_auto['soap:Envelope']['soap:Body']['ns2:validarComprobanteResponse']['RespuestaRecepcionComprobante']
		#print("Información Adicional:", informacion_adicional)
		#print("estado:", estado)
		
		claveAccesoComprobante = doc_data.claveAcceso

		response_xml_data_string = ""
		
		message_identificador = ''
		message_text = ''		

		if(response_valida['estado'] == 'DEVUELTA'):
			if (response_valida['comprobantes']['comprobante']['mensajes']['mensaje']['tipo'] == "ERROR"):
				if (response_valida['comprobantes']['comprobante']['mensajes']['mensaje']['identificador'] == "43" or 
					response_valida['comprobantes']['comprobante']['mensajes']['mensaje']['identificador'] == "65"):
					print('PROBAR AUTORIZACION PORQUE PARECE YA AUTORIZADA')
					message_identificador = response_valida['comprobantes']['comprobante']['mensajes']['mensaje']['identificador']
					message_text = response_valida['comprobantes']['comprobante']['mensajes']['mensaje']['mensaje']
					
					response_auto = processAuthorization(doc_data, 
						 typeDocSri, 
						 doctype_erpnext, 
						 sri_environment, 
						 claveAccesoComprobante, 
						 server_timeout, 
						 response_xml_data_string, 
						 message_identificador,
						 message_text)
					
					return response_auto

				else:
					print('ACTUALIZAR EL ESTADO DE DOCUMENTO l1')
					
					response_xml_data_string = response.text

					registerResponse_native(doc_data, typeDocSri, doctype_erpnext, 
							 response_valida, #response_valida_json_auto, 
							 response_xml_data_string)

					#response['ok'] = False
					response_valida['ok'] = False
					return response_valida
					#return response
			else:
				pass

		if(response_valida['estado'] == 'ERROR'):
			print('ACTUALIZAR EL ESTADO DE DOCUMENTO l2')
			#response['ok'] = False
			response_valida['ok'] = False
			return response_valida
			#return json.dumps(respuestaRecepcion)
			#return response

		if(response_valida['estado'] == 'RECIBIDA'):
			print('ACTUALIZAR EL ESTADO DE DOCUMENTO l3')
		
			#SE REQUIERE METODO PARA CREAR LA CLAVE DE ACCESO	

			response_auto = processAuthorization(doc_data, 
							typeDocSri, 
							doctype_erpnext, 
							sri_environment, 
							claveAccesoComprobante, 
							server_timeout, 
							response_xml_data_string, 
							message_identificador,
							message_text)
		
			return response_auto

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
	if typeDocSri ==  "FAC":
			document_object = frappe.get_last_doc('Sales Invoice', filters = { 'name': doc.name })
			if(document_object):
				document_object.db_set('numeroautorizacion', response_json.data.autorizaciones.autorizacion[0].numeroAutorizacion)
				document_object.db_set('sri_estado', 200)
				document_object.db_set('sri_response', response_json.data.autorizaciones.autorizacion[0].estado)
				#TODO: Corregir
				document_object.db_set('docidsri', doc.estab + "-" + doc.ptoemi + "-" + '{:09d}'.format(doc.secuencial) )

				#fechaAutorizacion = parser.parse(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)

				print(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)

				fecha_string = response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion				
				#fecha_con_zona = datetime.strptime(fecha_string, "%Y-%m-%dT%H:%M:%S")
				fecha_con_zona = parser.parse(fecha_string)

				#datetime.fromisoformat NO COMPATIBLE CON PYTHON 3.6
				#fecha_con_zona = datetime.fromisoformat(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)
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
	
	elif typeDocSri ==  "GRS":
			
			print(response_json)

			document_object = frappe.get_last_doc('Delivery Note', filters = { 'name': doc.name })
			if(document_object):				
				document_object.db_set('numeroautorizacion', response_json.data.autorizaciones.autorizacion[0].numeroAutorizacion)
				document_object.db_set('sri_estado', 200)
				document_object.db_set('sri_response', response_json.data.autorizaciones.autorizacion[0].estado)
				#document_object.db_set('docidsri', doc.estab + "-" + doc.ptoemi + "-" + '{:09d}'.format(doc.secuencial) )

				fechaAutorizacion = parser.parse(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)
				#fecha_con_zona = datetime.fromisoformat(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)
				# Eliminar la zona horaria
				#fechaAutorizacion = fecha_con_zona.replace(tzinfo=None)

				#print(fechaAutorizacion)
				#print(type(fechaAutorizacion))
				#print(datetime.now())
				#print(type(datetime.now()))

				document_object.db_set('fechaautorizacion', fechaAutorizacion)

	elif typeDocSri ==  "CRE":
			print(response_json)
			document_object = frappe.get_last_doc('Purchase Withholding Sri Ec', filters = { 'name': doc.name })
			if(document_object):				
				document_object.db_set('numeroAutorizacion', response_json.data.autorizaciones.autorizacion[0].numeroAutorizacion)
				document_object.db_set('sri_estado', 200)
				document_object.db_set('sri_response', response_json.data.autorizaciones.autorizacion[0].estado)
				document_object.db_set('numDoc', doc.estab + "-" + doc.ptoemi + "-" + '{:09d}'.format(doc.secuencial))
				fechaAutorizacion = parser.parse(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)				
				document_object.db_set('fechaAutorizacion', fechaAutorizacion)   

def registerResponse_native(doc, typeDocSri, doctype_erpnext, response_json, response_json_text):
	#TODO: El XML se guarda de forma incorrecta, pero al parecer es un comportamiento normal
	# del frappe, hay que verificar.
	sri_status = ''

	#Si es que tiene itemes de autorizaciones
	if('autorizaciones' in response_json):
		sri_status = response_json['autorizaciones']['autorizacion']['estado']

	if('estado' in response_json):
		sri_status = response_json['estado']

	xml_response_new = frappe.get_doc({
					'doctype': 'Xml Responses',
					'doc_ref': doc.name,
					#'xmldata': response_json.autorizaciones.autorizacion[0].comprobante,
					'xmldata': response_json_text,
					'sri_status': sri_status,
					'tip_doc': typeDocSri,
					'doc_type': doctype_erpnext
				})

	xml_response_new.insert()
	frappe.db.commit()

def updateStatusDocument_native(doc, typeDocSri, response_json):
	if typeDocSri ==  "FAC":
			document_object = frappe.get_last_doc('Sales Invoice', filters = { 'name': doc.name })
			if(document_object):
				document_object.db_set('numeroautorizacion', response_json['autorizaciones']['autorizacion']['numeroAutorizacion'])
				document_object.db_set('sri_estado', 200)
				document_object.db_set('sri_response', response_json['autorizaciones']['autorizacion']['estado'])
				#TODO: Corregir
				document_object.db_set('docidsri', doc.estab + "-" + doc.ptoemi + "-" + '{:09d}'.format(doc.secuencial) )

				#fechaAutorizacion = parser.parse(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)

				print(response_json['autorizaciones']['autorizacion']['fechaAutorizacion'])

				fecha_string = response_json['autorizaciones']['autorizacion']['fechaAutorizacion']				
				#fecha_con_zona = datetime.strptime(fecha_string, "%Y-%m-%dT%H:%M:%S")
				fecha_con_zona = parser.parse(fecha_string)

				#datetime.fromisoformat NO COMPATIBLE CON PYTHON 3.6
				#fecha_con_zona = datetime.fromisoformat(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)
				# Eliminar la zona horaria
				fechaAutorizacion = fecha_con_zona.replace(tzinfo=None)

				document_object.db_set('fechaautorizacion', fechaAutorizacion)
				#document_object.db_set('fechaautorizacion', datetime.now())
				
				#NO ES NECESARIO EJECUTAR SAVE
				#document_object.save(
				#	ignore_permissions=True, # ignore write permissions during insert
				#	ignore_version=True # do not create a version record
				#)
	
	elif typeDocSri ==  "GRS":
			
			print(response_json)

			document_object = frappe.get_last_doc('Delivery Note', filters = { 'name': doc.name })
			if(document_object):				
				document_object.db_set('numeroautorizacion', response_json.data.autorizaciones.autorizacion[0].numeroAutorizacion)
				document_object.db_set('sri_estado', 200)
				document_object.db_set('sri_response', response_json.data.autorizaciones.autorizacion[0].estado)
				#document_object.db_set('docidsri', doc.estab + "-" + doc.ptoemi + "-" + '{:09d}'.format(doc.secuencial) )

				fechaAutorizacion = parser.parse(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)
				#fecha_con_zona = datetime.fromisoformat(response_json.data.autorizaciones.autorizacion[0].fechaAutorizacion)
				# Eliminar la zona horaria
				#fechaAutorizacion = fecha_con_zona.replace(tzinfo=None)

				#print(fechaAutorizacion)
				#print(type(fechaAutorizacion))
				#print(datetime.now())
				#print(type(datetime.now()))

				document_object.db_set('fechaautorizacion', fechaAutorizacion)

	elif typeDocSri ==  "CRE":
			print(response_json)
			document_object = frappe.get_last_doc('Purchase Withholding Sri Ec', filters = { 'name': doc.name })
			if(document_object):
				document_object.db_set('numeroAutorizacion', response_json['autorizaciones']['autorizacion']['numeroAutorizacion'])
				document_object.db_set('sri_estado', 200)
				document_object.db_set('sri_response', response_json['autorizaciones']['autorizacion']['estado'])				
				document_object.db_set('numDoc', doc.estab + "-" + doc.ptoemi + "-" + '{:09d}'.format(doc.secuencial) )
				fecha_string = response_json['autorizaciones']['autorizacion']['fechaAutorizacion']				
				fecha_con_zona = parser.parse(fecha_string)
				fechaAutorizacion = fecha_con_zona.replace(tzinfo=None)
				document_object.db_set('fechaautorizacion', fechaAutorizacion)

