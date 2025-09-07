from __future__ import unicode_literals
import os
import frappe
import json

def get_last_sequencial_found(company_id, sri_type_doc_lnk, establishment, ptoemi):
	if sri_type_doc_lnk == "FAC":
			#'sri_environment_lnk': sri_environment_lnk,
			# TODO: Agregar "ambiente" en las tablas
			docs_found = frappe.get_list("Sales Invoice",  fields=[f"MAX(secuencial) as max_secuencial"], filters={        	
				'company': company_id,
                'estab': establishment,
                'ptoemi': ptoemi,
    		})
			#print(docs_found)
			#print(docs_found[0].max_secuencial)
			return docs_found[0].max_secuencial			
		#elif sri_type_doc_lnk ==  "GRS":
		#elif sri_type_doc_lnk ==  "CRE":
	if sri_type_doc_lnk == "GRS":
		docs_found = frappe.get_list("Delivery Note",  fields=[f"MAX(secuencial) as max_secuencial"], filters={        	
				'company': company_id,
    		})
		return docs_found[0].max_secuencial
	
	if sri_type_doc_lnk == "CRE":
		docs_found = frappe.get_list("Purchase Withholding Sri Ec",  fields=[f"MAX(secuencial) as max_secuencial"], filters={        	
				'company': company_id,
    		})
		return docs_found[0].max_secuencial
     
def insert_update(DocTypeName, JsonPath):
    print("insert_update_data")
    # Lee el archivo JSON
    with open(JsonPath, 'r') as file:
        contenido_json_modificado = file.read()

    default_company = frappe.defaults.get_user_default("Company") # compañía por defecto
    print("Company:", default_company)

    data = json.loads(contenido_json_modificado)

    # Itera sobre los registros en el JSON e inserta/actualiza
    for record in data:
        record["company_link"] = default_company   # <- ojo: tu DocType tiene este campo
        record["name"] = record["name"].replace("*","")

        print("Procesando:", record["name"])

        try:
            existing = frappe.get_all(
                DocTypeName,
                filters={"record_name": record["record_name"]},
                fields=["name"]
            )

            if existing:
                # Actualizar documento existente
                document_object = frappe.get_doc(DocTypeName, existing[0].name)
                print("Actualizando:", record["name"])

                # Actualizamos campos simples
                for key, value in record.items():
                    if key not in ["sri_ptoemi_detail", "name"]:  # child table se maneja aparte
                        setattr(document_object, key, value)

                # Actualizamos tabla hija (si viene en el JSON)
                if "sri_ptoemi_detail" in record:
                    document_object.sri_ptoemi_detail = []  # limpia antes de recargar
                    for child in record["sri_ptoemi_detail"]:
                        sales_invoice_max = get_last_sequencial_found(record["company_link"], 'FAC', record["name"], child['record_name'])
                        if sales_invoice_max is None:
                            sales_invoice_max = 0
                        
                        delivery_note_max = get_last_sequencial_found(record["company_link"], 'GRS', record["name"], child['record_name'])
                        if delivery_note_max is None:
                            delivery_note_max = 0
                        
                        purchase_withholding_max = get_last_sequencial_found(record["company_link"], 'CRE', record["name"], child['record_name'])                        
                        if purchase_withholding_max is None:
                            purchase_withholding_max = 0

                        child['sec_factura'] = sales_invoice_max
                        child['sec_guiaremision'] = delivery_note_max
                        child['sec_comprobanteretencion'] = purchase_withholding_max

                        document_object.append("sri_ptoemi_detail", child)

                document_object.save()
            else:
                # Crear nuevo documento
                print("Creando:", record.get("name", "<sin name>"))
                new_doc = frappe.get_doc(record)                
                new_doc.insert(ignore_permissions=True)

            frappe.db.commit()

        except Exception as e:
            print("❌ Error en registro:", record["name"], "-", str(e))
            frappe.db.rollback()  # rollback solo el registro fallido, no todo el lote

    print("Proceso terminado inser_update.")

def execute():
    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))

    source_list = [
        {
            "doctype" : "Sri Establishment",
            "json_file" : "sri_establishment.json",
            "action":"update"
        },        
    ]

    for source_item in source_list:
        print(source_item)
        filepathfull = os.path.join(dir_path, "../../fixtures/specials", source_item['json_file'])
        
        try:            
            if source_item["action"] == "update":
                insert_update(source_item["doctype"], filepathfull)
        except Exception as e:
            return {"message": "Failed import.", "error": str(e)}
