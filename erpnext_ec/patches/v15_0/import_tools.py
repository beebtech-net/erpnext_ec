from __future__ import unicode_literals
import os
import frappe
import json

def insert_new_data(DocTypeName, JsonPath):
    # Lee el archivo JSON
    with open(JsonPath, 'r') as file:
        contenido_json = file.read()
        contenido_json_modificado = contenido_json

        default_company = frappe.defaults.get_user_default("Company") #se obtiene compañia por defecto
        print(default_company)

        data = json.loads(contenido_json_modificado)
        #data = json.load(file)

    # Itera sobre los registros en el JSON e inserta en el DocType
    for record in data:
        record["company"] = default_company
        pasivo_circulante_account = '' # buscar en la base de datos la cuenta que vaya a ser padre
        print(record['parent_account'])
        print("*" in record['parent_account'])

        #La busqueda de la cuenta de pasivo circulante
        if("*" in record['parent_account']):
            #resulParentAccount = frappe.get_all("Account", filters={"name": record['parent_account']})
            parent_account_search = record['parent_account'].replace("*","")
            print(parent_account_search)
            resulParentAccount = frappe.get_all("Account", filters={"name": ["like", "%" + parent_account_search + "%"]})
            print(resulParentAccount)
            print("CUENTA DE PASIVO!!")
            
            if resulParentAccount:
                pasivo_circulante_account=resulParentAccount[0].name
                record["parent_account"] = pasivo_circulante_account
                record["parent"] = pasivo_circulante_account
                
                try:
                    #CREACION DE SUBCUENTA DE RETENCIONES
                    resulRetenAccount = frappe.get_all("Account", filters={"name": ["like", "%" + record["account_name"] + "%"]})
                    print(resulRetenAccount)
                    if(resulRetenAccount):
                        print("Ya existente: " + record["account_name"])
                    else:
                        doc = frappe.new_doc(DocTypeName)
                        doc.update(record)
                        print("REGISTRO NUEVO")
                        print(doc)
                        doc.insert()
                    
                    #Continua con las siguientes subcuentas
                    continue
                except Exception as e:
                    print("Error:" + e)
        
                continue                

    print("Registros insertados exitosamente.")


def update_data(DocTypeName, JsonPath):
    print("update_data")
    # Lee el archivo JSON
    with open(JsonPath, 'r') as file:
        contenido_json = file.read()
        contenido_json_modificado = contenido_json

        default_company = frappe.defaults.get_user_default("Company") #se obtiene compañia por defecto
        print(default_company)

        data = json.loads(contenido_json_modificado)
        #data = json.load(file)

    # Itera sobre los registros en el JSON e inserta en el DocType
    for record in data:
        record["company"] = default_company
        #pasivo_circulante_account = '' # buscar en la base de datos la cuenta que vaya a ser padre
        #print(record['parent_account'])
        #print("*" in record['parent_account'])
        
        try:
            record["account_name"] = record['account_name'].replace("*","")
            print(record["account_name"])
            #CREACION DE SUBCUENTA DE RETENCIONES
            #resulRetenAccount = frappe.get_all("Account", filters={"name": ["like", "%" + record["account_name"] + "%"]})
            
            document_object = frappe.get_last_doc('Account', filters={"name": ["like", "%" + record["account_name"] + "%"]})

            #document_object = frappe.get_last_doc('Account', filters={"name": ["like", "%" + record["account_name"] + "%"],
            #                                                          "company":record["company"]})
            
            print(document_object)
            
            #Realiza modificaciones en la base solo si los datos no coinciden
            if(not document_object.sricodeper == record["sricodeper"]):
                document_object.db_set('sricodeper', record["sricodeper"])

            if(not document_object.sricode == record["sricode"]):
                document_object.db_set('sricode', record["sricode"])           
            
            #No funcionará porque estan dentro de un Try
            #raise ReferenceError("Error de prueba")
        
        except Exception as e:
            print("Error:" + e)

        continue


#def import_batch_special():
def execute():

    cwd = os.getcwd()
    dir_path = os.path.dirname(os.path.realpath(__file__))

    source_list = [
        {
                "doctype" : "Account",
                "json_file" : "account_insert.json",
                "action":"insert"
        },
        {
                "doctype" : "Account",
                "json_file" : "account_update.json",
                "action":"update"
        }
	]

    for source_item in source_list:
        print (source_item)
        filepathfull = dir_path + "/../../fixtures/specials/" + source_item['json_file']
        
        try:
            if(source_item["action"] == "insert"):
                insert_new_data(source_item["doctype"], filepathfull)

            if(source_item["action"] == "update"):
                update_data(source_item["doctype"], filepathfull)
        except Exception as e:
            return {"message": "Failed import.", "error": str(e)}
    