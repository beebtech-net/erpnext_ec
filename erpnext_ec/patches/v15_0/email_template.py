from __future__ import unicode_literals
from frappe import __version__ as frappe_version
import frappe
import json
import os
#from frappe.utils import validate_email_address, split_emails
#import click
# from ec_extend.setup import after_install as setup

def execute():
	
	cwd = os.getcwd()
	dir_path = os.path.dirname(os.path.realpath(__file__))
	
	script_list = [
            {
                  "doc_type" : "Sales Invoice",
                  "name" : "Factura SRI Body",
                  "module" : "Accounts",
				  "standard": "No",
				  "custom_format": True,
				  "print_format_type": "Jinja",
				  "default_print_language":"es-EC",
                  "source_path" : "sales_invoice_sri_email.html",
				  "disabled": 0,
				  "raw_printing": 0,
			},					
	]
    
	for script_item in script_list:
		print (script_item)
		with open(dir_path + "/../../public/jinja/" + script_item['source_path']) as f:			
			data = f.read()
			#data = data.replace('[DOCTYPE_CUSTOM_FORM_SRI]',script_item['doc_type'])
		create_email_template(script_item, data)

def create_email_template(doc_data, template_content):
		
    #from frappe.core.page.permission_manager.permission_manager import add
	resultData = frappe.get_all("Email Template", filters={"name": doc_data['name']})

	#if not frappe.get_all("Client Script", filters={"name": script_name}):
	if resultData:
		#resultData.remove()
		frappe.delete_doc("Email Template", doc_data['name'])

    # Define el documento Client Script en formato JSON
	client_script_data = {
			"docstatus": 0,
			"doctype": "Email Template",
			"name": doc_data['name'],
			"use_html": True,
			"subject":"EMAIL YUO",
			"response_html": template_content
		}

    # Crea un nuevo documento Client Script usando el ORM de Frappe
	new_client_script = frappe.get_doc(client_script_data)
	new_client_script.insert()

    # Guarda el documento
	new_client_script.save()

	print("Instalando Email Template " + doc_data['name'])
    #add("Client Script","All", script_path)
