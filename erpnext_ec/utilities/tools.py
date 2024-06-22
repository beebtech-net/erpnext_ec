import frappe
import socket

@frappe.whitelist()
def get_full_url():
    # Obtener el nombre del host desde la solicitud actual
    host_name = frappe.utils.get_host_name_from_request()

    # Verificar si está en modo DNS multitenant
    if frappe.local.conf.get('dns_multitenant'):
        # Usar el puerto configurado en caso de multitenancy
        port = frappe.conf.get('webserver_port', 8000)  # Puerto por defecto 8000
    else:
        # Obtener el puerto configurado o usar un puerto por defecto
        port = frappe.conf.http_port if hasattr(frappe.conf, 'http_port') else 80

    # Construir la URL completa con el protocolo y el puerto
    protocol = "https://" if frappe.local.request.scheme == "https" else "http://"
    full_url = f"{protocol}{host_name}:{port}"

    return full_url
