import frappe
import socket
from erpnext_ec.utilities.sri_ws import verify_signature
import json
from datetime import datetime

@frappe.whitelist()
def get_full_url():
    # Obtener el nombre del host desde la solicitud actual
    host_name = frappe.utils.get_host_name_from_request()
    port = ''

    # Verificar si está en modo DNS multitenant
    if not frappe.local.conf.get('dns_multitenant'):    
        port = ':' + str(frappe.local.conf.nginx_port)

    # Construir la URL completa con el protocolo y el puerto
    full_url = f"{host_name}{port}"

    return full_url


@frappe.whitelist(allow_guest=True)
def set_cookie(cookie_name, cookie_value):
    frappe.local.cookie_manager.set_cookie(cookie_name, cookie_value)    
    return '{status}'

#Esta función servirá para evaluar la configuración actual del sistem
# y determinar si es que esta apta para empezar a realizar documentos
# electrónicos del SRI
@frappe.whitelist(allow_guest=True)
def validate_sri_settings():
    result = {}
    header = []
    alerts = []
    SettingsAreReady = True

    company_object = frappe.get_all('Company',fields=["*"],)
    print('-----------------------------------')
    print(company_object)

    for company_item in company_object:
        header.append({"index": 0, "description": "Empresa", "value": company_item.name})
        
        print(company_item.sri_active_environment)
        #sri_environment = frappe.get_last_doc('Sri Environment', filters = { 'name': company_item.sri_active_environment })
        #print(sri_environment)

        if (company_item.sri_active_environment):
            #print(sri_environment.name)
            #print(sri_environment.id)
            header.append({"index": 0, "description": "Ambiente", "value": company_item.sri_active_environment})
        else:
            alerts.append({"index": 0, "description": "Ambiente de SRI no seleccionado", "type":"error"})
            SettingsAreReady = False
            

        #regional_settings_ec = frappe.get_last_doc('Regional Settings Ec', filters = { 'name': company_item.regional_settings_ec })
        if(company_item.regional_settings_ec):
            header.append({"index": 0, "description": "Configuración", "value": company_item.regional_settings_ec})
        else:
            alerts.append({"index": 0, "description": "Configuración no seleccionada", "type":"error"})
            SettingsAreReady = False

        #print(regional_settings_ec)
        #print('regional_settings_ec.signature_tool')
        #print(regional_settings_ec.signature_tool)

        sri_sequences = frappe.get_all('Sri Sequence', filters = { 'company_id': company_item.name })
        #print('Secuencias')
        #print(len(sri_sequences))
        if(len(sri_sequences)==0):
            #print('SE REQUIERE CREAR SECUENCIAS para' + company_item.name)
            alerts.append({"index": 0, "description": "Secuencias no creadas", "help":"Vaya a Secuencias SRI y haga clic en el botón 'Crear Secuencias''", "type":"error"})
            SettingsAreReady = False
        else:
            header.append({"index": 0, "description": "Secuencias SRI", "value": len(sri_sequences)})

        print_formats = frappe.get_all('Print Format', filters = { "name": ["in", ['Factura SRI','Retención SRI','Guía de Remisión SRI']] })
        #print('---------PRINTS')
        #print(print_formats)
        if(len(print_formats)==0):
            #print('SIN FORMATOS')
            alerts.append({"index": 0, 
                           "description": "Formatos de Impresión no creados", 
                           "help":"Vaya a Formatos de Impresión y haga clic en el botón 'Crear Secuencias''", 
                           "type":"error"})
            SettingsAreReady = False
        else:
            header.append({"index": 0, "description": "Formatos de impresión", "value": len(print_formats)})

        accounts = frappe.get_all('Account', 
                                       filters = [
                ["sricode", "!=", "0"],
                ["sricode", "is", "set"],
                ["sricode", "!=", ""]
            ])

        if(len(accounts)==0):            
            alerts.append({"index": 0, 
                           "description": "Cuentas contables para SRI no creados", 
                           "help":"Vaya a Cuentas Contables y haga clic en el botón 'Crear Datos SRI', o cree los datos de forma manual.", 
                           "type":"error"})
            SettingsAreReady = False
        else:
            header.append({"index": 0, "description": "Cuentas contables para SRI", "value": len(accounts)})

        #Si es que se ha seleccionado firma electrónica
        if(company_item.sri_signature):
            sri_signature = frappe.get_all('Sri Signature', 
                                        filters = [
                    ["name", "=", company_item.sri_signature]
                ])

            #if(len(sri_signature)==0):                
            #else:
            #    header.append({"index": 0, "description": "Cuentas contables para SRI", "value": len(sri_signature)})
            header.append({"index": 0, "description": "Firma Electrónica seleccionada", "value": company_item.sri_signature})
            if(sri_signature and len(sri_signature) > 0):
                first_record = sri_signature[0]
                first_record_json = json.dumps(first_record, indent=4)
                verify_data = verify_signature(first_record_json)
                print('===============================')
                print(verify_data)
                expiry_date = verify_data['not_valid_after']

                # Obtener la fecha actual
                current_date = datetime.now()

                expiry_date_str = expiry_date.strftime("%Y-%m-%d %H:%M:%S")
                # Comparar las fechas
                if expiry_date < current_date:
                    #print("La fecha está expirada.")
                    alerts.append({"index": 0,
                            "description": f"Firma Electrónica expirada {expiry_date_str}", 
                            "help": f"Debe emitir una nueva firma electrónica.", 
                            "type": "error"})
                    SettingsAreReady = False
                else:                    
                    header.append({"index": 0, "description": "Firma Electrónica fecha expiración", "value": expiry_date_str})
        else:
            alerts.append({"index": 0,
                            "description": "Firma Electrónica no seleccionada", 
                            "help": f"Vaya a Compañia {company_item.name} y seleccione una firma electrónica válida.", 
                            "type":"error"})
            SettingsAreReady = False
        
    result = {
        "header": header,
        "alerts": alerts,
        #"doctype_erpnext": doctype_erpnext,
        #"typeDocSri": "typeDocSri",
        "SettingsAreReady": SettingsAreReady
    }

    if(not SettingsAreReady):
        #print(result)
        create_notification_log(
            user="administrator",
            subject="Configuración incompatible con el SRI",
            body="Revise la configuración del sistema y corrija para poder crear documentos electrónicos compatibles con el SRI."
        )

    return result

@frappe.whitelist(allow_guest=True)
def on_login_auto():
    set_cookie('login_boot', 'yes')
    set_cookie('sri_settings_alert', '0')


def create_notification_log(user, subject, body):
    # Crear un nuevo documento de Notification Log
    notification_log = frappe.get_doc({
        "doctype": "Notification Log",
        "subject": subject,
        "email_content": body,
        "type": "Alert",  # Tipos: Alert, Warning, Error, Success
        "for_user": user,
        "document_type": "",
        "document_name": "",  # Nombre del documento relacionado
        "from_user": frappe.session.user,
        "read": 0,  # 0 = no leído, 1 = leído
        "timeline_doctype": "Custom Doctype",  # Tipo de documento en la línea de tiempo
        "timeline_name": "12345",  # Nombre del documento en la línea de tiempo
    })
    
    # Guardar el documento en la base de datos
    notification_log.insert(ignore_permissions=True)
    
    # Confirmar los cambios
    frappe.db.commit()

