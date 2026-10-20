from __future__ import unicode_literals
import frappe
import json

from erpnext_ec.utilities.secure_reader import read_file_in_app

def insert_new_data(DocTypeName, contenido_json):
    # Ya no recibe una ruta: recibe el contenido ya leído y validado
    contenido_json_modificado = contenido_json

    default_company = frappe.defaults.get_user_default("Company")
    frappe.logger().info(default_company)

    data = json.loads(contenido_json_modificado)

    for record in data:
        record["company"] = default_company
        pasivo_circulante_account = ''
        frappe.logger().info(record['parent_account'])
        frappe.logger().info("*" in record['parent_account'])

        # La busqueda de la cuenta de pasivo circulante
        if "*" in record['parent_account']:
            parent_account_search = record['parent_account'].replace("*", "")
            frappe.logger().info(parent_account_search)
            resulParentAccount = frappe.get_all(
                "Account",
                filters={"name": ["like", "%" + parent_account_search + "%"]}
            )
            frappe.logger().info(resulParentAccount)
            frappe.logger().info("CUENTA DE PASIVO!!")

            if resulParentAccount:
                pasivo_circulante_account = resulParentAccount[0].name
                record["parent_account"] = pasivo_circulante_account
                record["parent"] = pasivo_circulante_account

                try:
                    # CREACION DE SUBCUENTA DE RETENCIONES
                    resulRetenAccount = frappe.get_all(
                        "Account",
                        filters={"name": ["like", "%" + record["account_name"] + "%"]}
                    )
                    frappe.logger().info(resulRetenAccount)
                    if resulRetenAccount:
                        frappe.logger().info("Ya existente: " + record["account_name"])
                    else:
                        doc = frappe.new_doc(DocTypeName)
                        doc.update(record)
                        frappe.logger().info("REGISTRO NUEVO")
                        frappe.logger().info(doc)
                        doc.insert()

                    # Continua con las siguientes subcuentas
                    continue
                except Exception as e:
                    frappe.logger().error(str(e))

                continue

    frappe.logger().info("Registros insertados exitosamente.")


def update_data(DocTypeName, contenido_json):
    frappe.logger().info("update_data")
    # Ya no recibe una ruta: recibe el contenido ya leído y validado
    contenido_json_modificado = contenido_json

    default_company = frappe.defaults.get_user_default("Company")
    frappe.logger().info(default_company)

    data = json.loads(contenido_json_modificado)

    for record in data:
        record["company"] = default_company

        try:
            record["account_name"] = record['account_name'].replace("*", "")
            frappe.logger().info(record["account_name"])

            document_object = frappe.get_last_doc(
                'Account',
                filters={"name": ["like", "%" + record["account_name"] + "%"]}
            )

            frappe.logger().info(document_object)

            # Realiza modificaciones en la base solo si los datos no coinciden
            if not document_object.codigoporcentaje == record["codigoporcentaje"]:
                document_object.db_set('codigoporcentaje', record["codigoporcentaje"])

            if not document_object.sricode == record["sricode"]:
                document_object.db_set('sricode', record["sricode"])

        except Exception as e:
            frappe.logger().error(str(e))

        continue


def execute():
    source_list = [
        {
            "doctype": "Account",
            "json_file": "account_insert.json",
            "action": "insert"
        },
        {
            "doctype": "Account",
            "json_file": "account_update.json",
            "action": "update"
        }
    ]

    for source_item in source_list:
        frappe.logger().info(source_item)

        try:
            # El helper valida la ruta y devuelve el contenido
            contenido_json = read_file_in_app(
                "erpnext_ec",
                "fixtures",
                "specials",
                source_item["json_file"]
            )

            if source_item["action"] == "insert":
                insert_new_data(source_item["doctype"], contenido_json)

            if source_item["action"] == "update":
                update_data(source_item["doctype"], contenido_json)

        except Exception as e:
            return {"message": "Failed import.", "error": str(e)}