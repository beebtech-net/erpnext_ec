# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from datetime import datetime, date, timedelta
import time
import frappe
from frappe import _
import erpnext
#from frappe.utils.pdf import get_pdf

import json
from types import SimpleNamespace

from erpnext_ec.patches.v15_0 import print_formats 

@frappe.whitelist()
def load_print_format_sri():
	print_formats.execute()
	print('Terminada la importación de formatos de impresión para el SRI')
	pass

@frappe.whitelist()
def load_sri_sequences(company):
	#company_id = 1
	#company='BeebTech'
	if not company:
		raise ReferenceError("El parámetro de la empresa es requerido")
	
	data = [
		{
			"doctype": "Sri Sequence",
			"name": "FAC-DES",
			"id": 1,
			"sri_environment_lnk": "DES",
			"sri_type_doc_lnk":"FAC",
			"value": 0,
			"description": "Secuencial para FACTURAS DESARROLLO",
			"company_id": company
		},
		{
			"doctype": "Sri Sequence",
			"name": "FAC-PRO",
			"id": 2,
			"sri_environment_lnk": "PRO",
			"sri_type_doc_lnk":"FAC",
			"value": 0,
			"description": "Secuencial para FACTURAS PRODUCCION",
			"company_id": company
		},
		{
			"doctype": "Sri Sequence",
			"name": "NCR-DES",
			"id": 3,
			"sri_environment_lnk": "DES",
			"sri_type_doc_lnk":"NCR",
			"value": 0,
			"description": "Secuencial para NOTCRED DESARROLLO",
			"company_id": company
		},
		{
			"doctype": "Sri Sequence",
			"name": "NCR-PRO",
			"id": 4,
			"sri_environment_lnk": "PRO",
			"sri_type_doc_lnk":"NCR",
			"value": 0,
			"description": "Secuencial para NOTCRED PRODUCCION",
			"company_id": company
		},
		{
			"doctype": "Sri Sequence",
			"name": "NDE-DES",
			"id": 5,
			"sri_environment_lnk": "DES",
			"sri_type_doc_lnk":"NDE",
			"value": 0,
			"description": "Secuencial para NOTDEB DESARROLLO",
			"company_id": company
		},
		{
			"doctype": "Sri Sequence",
			"name": "NDE-PRO",
			"id": 6,
			"sri_environment_lnk": "PRO",
			"sri_type_doc_lnk":"NDE",
			"value": 0,
			"description": "Secuencial para NOTDEB PRODUCCION",
			"company_id": company
		},
		{
			"doctype": "Sri Sequence",
			"name": "GRS-DES",
			"id": 7,
			"sri_environment_lnk": "DES",
			"sri_type_doc_lnk":"GRS",
			"value": 0,
			"description": "Secuencial para Guia Remis DESARROLLO",
			"company_id": company
		},
		{
			"doctype": "Sri Sequence",
			"name": "GRS-PRO",
			"id": 8,
			"sri_environment_lnk": "PRO",
			"sri_type_doc_lnk":"GRS",
			"value": 0,
			"description": "Secuencial para Guia Remis PRODUCCION",
			"company_id": company
		},
		{
			"doctype": "Sri Sequence",
			"name": "CRE-DES",
			"id": 9,
			"sri_environment_lnk": "DES",
			"sri_type_doc_lnk":"CRE",
			"value": 0,
			"description": "Secuencial para Comp. Reten. DESARROLLO",
			"company_id": company
		},
		{
			"doctype": "Sri Sequence",
			"name": "CRE-PRO",
			"id": 10,
			"sri_environment_lnk": "PRO",
			"sri_type_doc_lnk":"CRE",
			"value": 0,
			"description": "Secuencial para Comp. Reten. PRODUCCION",
			"company_id": company
		},
		{
			"doctype": "Sri Sequence",
			"name": "LIQ-DES",
			"id": 11,
			"sri_environment_lnk": "DES",
			"sri_type_doc_lnk":"LIQ",
			"value": 0,
			"description": "Secuencial para Liq. Comp. DESARROLLO",
			"company_id": company
		},
		{
			"doctype": "Sri Sequence",
			"name": "LIQ-PRO",
			"id": 12,
			"sri_environment_lnk": "PRO",
			"sri_type_doc_lnk":"LIQ",
			"value": 0,
			"description": "Secuencial para Liq. Comp. PRODUCCION",
			"company_id": company
		}
	]
	
	for record in data:
		#Aquí método para extraer el último secuencial encontrado, según el tipo de documento
		
		#docs_found = frappe.get_all("Sri Sequence", fields='*', filters={
        #'sri_environment_lnk': record['sri_environment_lnk'],
        #'sri_type_doc_lnk': record['sri_type_doc_lnk'],
		#'company_id': record['company_id'],
    	#})

		last_sequencial = get_last_sequencial_found(record['company_id'], record['sri_type_doc_lnk'], record['sri_environment_lnk'])

		try:
			docs_found = frappe.get_last_doc("Sri Sequence", filters={                
			'sri_environment_lnk': record['sri_environment_lnk'],
			'sri_type_doc_lnk': record['sri_type_doc_lnk'],        
			'company_id': record['company_id'],
			})

			#print(docs)
			
			if docs_found:
				print("Ya encontrado, no se creará registro")
				print(docs_found.sri_environment_lnk)
				print(docs_found.sri_type_doc_lnk)
				print(docs_found.company_id)				

				if(last_sequencial and last_sequencial > 0):
					#Eliminar y asignar nuevo secuencial
					docs_found.db_set('value', last_sequencial)			

				continue
		except frappe.DoesNotExistError:

			doc = frappe.get_doc({
			'doctype': record['doctype'],
			'name': record['name'],
			'sri_environment_lnk': record['sri_environment_lnk'],
			'sri_type_doc_lnk': record['sri_type_doc_lnk'],
			'value': last_sequencial,
			'description': record['description'],
			'company_id': record['company_id'],
			})

			doc.insert()
	
	frappe.db.commit()

	pass

def get_last_sequencial_found(company_id, sri_type_doc_lnk, sri_environment_lnk):
	match sri_type_doc_lnk:
		case "FAC":
			#'sri_environment_lnk': sri_environment_lnk,
			# TODO: Agregar "ambiente" en las tablas
			docs_found = frappe.get_list("Sales Invoice",  fields=[f"MAX(secuencial) as max_secuencial"], filters={        	
				'company': company_id,
    		})

			#print(docs_found)
			#print(docs_found[0].max_secuencial)
			return docs_found[0].max_secuencial			
		#case "GRS":
		#case "CRE":
			
			 
	

