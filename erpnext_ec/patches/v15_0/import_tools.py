from __future__ import unicode_literals
import os
import frappe
import json

def import_from_json(DocTypeName, JsonPath):
    # Lee el archivo JSON
    with open(JsonPath, 'r') as file:
        contenido_json = file.read()
        contenido_json_modificado = contenido_json;

        default_company = frappe.defaults.get_user_default("Company") #se obtiene compañia por defecto

        print(default_company)

        pasivo_circulante_account = '' # buscar en la base de datos la cuenta que vaya a ser padre

        #print(contenido_json)

        contenido_json_modificado = contenido_json_modificado.replace('{{company}}', default_company)
        contenido_json_modificado = contenido_json_modificado.replace('{{PasivoCirculante}}', pasivo_circulante_account)

        print(contenido_json_modificado)
        
        data = json.loads(contenido_json_modificado)
        #data = json.load(file)

    # Itera sobre los registros en el JSON e inserta en el DocType
    for record in data:
        doc = frappe.new_doc(DocTypeName)
        doc.update(record)
        doc.insert()

    print("Registros insertados exitosamente.")

def import_batch_special():

    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))

    source_list = [
        {
                "doctype" : "Account",
                "json_file" : "account_custom.json"
        }
	]

    for source_item in source_list:
        print (source_item)
        filepathfull = dir_path + "/../../fixtures/specials/" + source_item['json_file']
        try:
            import_from_json(source_item["doctype"], filepathfull)
        except Exception as e:
            return {"message": "Failed import.", "error": str(e)}
    