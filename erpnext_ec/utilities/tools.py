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
