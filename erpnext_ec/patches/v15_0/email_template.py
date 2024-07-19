from __future__ import unicode_literals
from frappe import __version__ as frappe_version
import frappe
import json
import os

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
                  "source_path" : "sales_invoice_sri_email.html",
				  "disabled": 0,
				  "subject": "Factura Electrónica -",
			},
			{
                  "doc_type" : "Sales Invoice",
                  "name" : "Nota de Crédito SRI Body",
                  "module" : "Accounts",
				  "standard": "No",
				  "custom_format": True,
                  "source_path" : "credit_note_sri_email.html",
				  "disabled": 0,
				  "subject": "Nota de Crédito -",
			},
			{
                  "doc_type" : "Delivery Note",
                  "name" : "Guia Remision Sri Body",
                  "module" : "Accounts",
				  "standard": "No",
				  "custom_format": True,
                  "source_path" : "delivery_note_sri_email.html",
				  "disabled": 0,
				  "subject": "Guía de Remisión -",
			},
			{
                  "doc_type" : "Purchase Withholding Sri Ec",
                  "name" : "Comprobante Retencion Sri Body",
                  "module" : "Accounts",
				  "standard": "No",
				  "custom_format": True,
                  "source_path" : "withdraw_purchase_sri_email.html",
				  "disabled": 0,
				  "subject": "Retención -",
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
    
	client_script_data = {
			"docstatus": 0,
			"doctype": "Email Template",
			"name": doc_data['name'],
			"use_html": 1,
			"subject": doc_data['subject'],
			"response_html": template_content,
			"owner":"Administrator"
		}
    
	new_client_script = frappe.get_doc(client_script_data)
	new_client_script.insert()
	new_client_script.save()

	print("Instalando Email Template " + doc_data['name'])
    #add("Client Script","All", script_path)
