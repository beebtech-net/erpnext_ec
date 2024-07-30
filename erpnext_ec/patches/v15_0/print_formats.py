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
                  "name" : "Factura SRI",
                  "module" : "Accounts",
				  "standard": "No",
				  "custom_format": True,
				  "print_format_type": "Jinja",
				  "default_print_language":"es-EC",
                  "source_path" : "sales_invoice_sri_ride.html",
				  "disabled": 0,
				  "raw_printing": 0,
			},
			{
                  "doc_type" : "Sales Invoice",
                  "name" : "Nota de Crédito SRI",
                  "module" : "Accounts",
				  "standard": "No",
				  "custom_format": True,
				  "print_format_type": "Jinja",
				  "default_print_language":"es-EC",
                  "source_path" : "credit_note_sri_ride.html",
				  "disabled": 0,
				  "raw_printing": 0,
			},
			{
                  "doc_type" : "Purchase Withholding Sri Ec",
                  "name" : "Retención SRI",
                  "module" : "Accounts",
				  "standard": "No",
				  "custom_format": True,
				  "print_format_type": "Jinja",
				  "default_print_language":"es-EC",
                  "source_path" : "withdraw_purchase_sri_ride.html",
				  "disabled": 0,
				  "raw_printing": 0,
			},
			{
                  "doc_type" : "Delivery Note",
                  "name" : "Guía de Remisión SRI",
                  "module" : "Accounts",
				  "standard": "No",
				  "custom_format": True,
				  "print_format_type": "Jinja",
				  "default_print_language":"es-EC",
                  "source_path" : "delivery_note_sri_ride.html",
				  "disabled": 0,
				  "raw_printing": 0,
			},
			{
                  "doc_type" : "Purchase Invoice",
                  "name" : "Liquidación de Compra SRI",
                  "module" : "Accounts",
				  "standard": "No",
				  "custom_format": True,
				  "print_format_type": "Jinja",
				  "default_print_language":"es-EC",
                  "source_path" : "purchase_settlement_sri_ride.html",
				  "disabled": 0,
				  "raw_printing": 0,
			},
	]
    
	print ("client_script")

	for script_item in script_list:
		print (script_item)
		with open(dir_path + "/../../public/jinja/" + script_item['source_path']) as f:			
			data = f.read()
			#data = data.replace('[DOCTYPE_CUSTOM_FORM_SRI]',script_item['doc_type'])
		create_print_format(script_item, data)

def create_print_format(doc_data, template_content):
	
    #from frappe.core.page.permission_manager.permission_manager import add
	resultData = frappe.get_all("Print Format", filters={"name": doc_data['name']})

	#if not frappe.get_all("Client Script", filters={"name": script_name}):
	if resultData:
		#resultData.remove()
		#frappe.delete_doc("Print Format", doc_data['name'])
		update_doc = frappe.get_doc("Print Format", doc_data['name'])
		update_doc.html = template_content
		update_doc.save()
		return
		

    # Define el documento Client Script en formato JSON
	client_script_data = {
			"docstatus": 0,
			"doctype": "Print Format",
			"name": doc_data['name'],
			"doc_type": doc_data['doc_type'],
			"module": doc_data['module'],
			"print_format_type": doc_data['print_format_type'],
			"default_print_language": doc_data['default_print_language'],

			"standard": doc_data['standard'],
			"custom_format": doc_data['custom_format'],

			"disabled": doc_data['disabled'],
			
			"html": template_content
		}

    # Crea un nuevo documento Client Script usando el ORM de Frappe
	new_client_script = frappe.get_doc(client_script_data)
	new_client_script.insert()

    # Guarda el documento
	new_client_script.save()

	print("Instalando Print Format " + doc_data['name'])
    #add("Client Script","All", script_path)
