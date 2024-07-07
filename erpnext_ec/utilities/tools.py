import frappe
import socket

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

@frappe.whitelist(allow_guest=True)
def validate_sri_settings():

    company_object = frappe.get_all('Company',fields=["*"],)
    print('-----------------------------------')
    print(company_object)

    for company_item in company_object:
        print(company_item.sri_active_environment)
        sri_environment = frappe.get_last_doc('Sri Environment', filters = { 'name': company_item.sri_active_environment })
        print(sri_environment)

        if (sri_environment):
            print(sri_environment.name)
            print(sri_environment.id)

        regional_settings_ec = frappe.get_last_doc('Regional Settings Ec', filters = { 'name': company_item.regional_settings_ec })
        print(regional_settings_ec)
        print('regional_settings_ec.signature_tool')
        print(regional_settings_ec.signature_tool)

        sri_sequences = frappe.get_all('Sri Sequence', filters = { 'company_id': company_item.name })
        print('Secuencias')
        print(len(sri_sequences))
        if(len(sri_sequences)==0):
            print('SE REQUIERE CREAR SECUENCIAS para' + company_item.name)

        print_formats = frappe.get_all('Print Format', filters = { "name": ["in", ['Factura SRI','Retención SRI','Guía de Remisión SRI']] })
        print('---------PRINTS')
        print(print_formats)
        if(len(print_formats)==0):
            print('SIN FORMATOS')
        
        print_formats = frappe.get_all('Account', filters = { "name": ["in", ['Factura SRI','Retención SRI','Guía de Remisión SRI']] })

    response_value = {
        "SettingsAreReady": False
    }

    return response_value

@frappe.whitelist(allow_guest=True)
def on_login_auto():
    set_cookie('login_boot', 'yes')
    set_cookie('sri_settings_alert', '0')


