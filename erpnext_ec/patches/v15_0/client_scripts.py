from __future__ import unicode_literals
from frappe import __version__ as frappe_version
import frappe
import json
import os
#from frappe.utils import validate_email_address, split_emails

import click
# from ec_extend.setup import after_install as setup

def execute():
	
	cwd = os.getcwd()
	dir_path = os.path.dirname(os.path.realpath(__file__))
	#print(dir_path)
	#print(cwd)
    
	# script_list = [
    #         {
    #               "doctype" : "Sales Invoice",
    #               "name" : "cs-erpnext-ec-si-list-001",
    #               "view" : "List",
    #               "source_path" : "sales_invoices_list_v15.js"
	# 		},
	# 		{
    #               "doctype" : "Sales Invoice",
    #               "name" : "cs-erpnext-ec-si-form-002",
    #               "view" : "Form",
    #               "source_path" : "sales_invoice_form.js"
	# 		}
	# ]


	script_list = [
            {
                  "doctype" : "Sales Invoice",
                  "name" : "cs-erpnext-ec-si-list-001",
                  "view" : "List",
                  "source_path" : "doctype_custom_list_sri.js"
			},
			{
                  "doctype" : "Sales Invoice",
                  "name" : "cs-erpnext-ec-si-form-002",
                  "view" : "Form",
                  "source_path" : "doctype_custom_form_sri.js"
			},
			{
                  "doctype" : "Delivery Note",
                  "name" : "cs-erpnext-ec-dn-list-003",
                  "view" : "List",
                  "source_path" : "doctype_custom_list_sri.js"
			},
			{
                  "doctype" : "Delivery Note",
                  "name" : "cs-erpnext-ec-dn-form-004",
                  "view" : "Form",
                  "source_path" : "doctype_custom_form_sri.js"
			}
	]
    
	print ("client_script")

	for script_item in script_list:
		print (script_item)
		with open(dir_path + "/../../public/js/" + script_item['source_path']) as f:			
			data = f.read()
			data = data.replace('[DOCTYPE_CUSTOM_FORM_SRI]',script_item['doctype'])
		assign_client_script_to_doctype(script_item['doctype'], script_item['name'], script_item['view'], data)


	#TODO: Arreglar la ruta relativa del js
	#with open("../apps/erpnext_ec/erpnext_ec/public/js/sales_invoices_list_v15.js") as f:
	#with open(dir_path + "/../public/js/sales_invoices_list_v15.js") as f:
	#	data = f.read()
	
	#print(data)

	#assign_client_script_to_doctype("Sales Invoice",
	#							 "cs-erpnext-ec-001",
	#							 data)

def assign_client_script_to_doctype(doctypeName, 
									script_name,
									view_target,
									script_content):
		
    #from frappe.core.page.permission_manager.permission_manager import add
	resultData = frappe.get_all("Client Script", filters={"name": script_name})

	#if not frappe.get_all("Client Script", filters={"name": script_name}):
	if resultData:
		#resultData.remove()
		frappe.delete_doc("Client Script", script_name)

    # Define el documento Client Script en formato JSON
	client_script_data = {
			"docstatus": 0,
			"doctype": "Client Script",
			"name": script_name,
			"__islocal": 1,
			"__unsaved": 1,
			"owner": "Administrator",
			"view": view_target,
			"enabled": 1,
			#"__newname": "Nom0001",
			"dt": doctypeName,
			"script": script_content
		}

    # Crea un nuevo documento Client Script usando el ORM de Frappe
	new_client_script = frappe.get_doc(client_script_data)
	new_client_script.insert()

    # Guarda el documento
	new_client_script.save()

	print("Instalando Client Script " + script_name)
    #add("Client Script","All", script_path)
