import frappe
import socket

@frappe.whitelist()
def get_full_url():
    # Obtener la URL base del sitio
    base_url = frappe.utils.get_url()
    
    # Verificar el protocolo
    if base_url.startswith("https://"):
        protocol = "https://"
    else:
        protocol = "http://"
    
    # Eliminar el protocolo de la URL base para obtener solo el host
    base_url = base_url.replace("https://", "").replace("http://", "")
    
    # Obtener el host del sitio actual
    current_site = frappe.local.site
    
    # Verificar si está en modo DNS multitenancy
    if frappe.local.conf.get('dns_multitenant'):
        host = current_site
        # Usar el puerto configurado en caso de multitenancy
        port = frappe.conf.get('webserver_port', 8000)  # Puerto por defecto 8000
    else:
        # Si no está en modo DNS multitenancy, usar la IP del host
        host = socket.gethostbyname(socket.gethostname())
        # Obtener el puerto configurado o usar un puerto por defecto
        port = frappe.conf.http_port if hasattr(frappe.conf, 'http_port') else 80
    
    # Construir la URL completa
    if port in [80, 443]:
        # Si el puerto es 80 o 443, no incluirlo en la URL
        full_url = f"{protocol}{host}"
    else:
        full_url = f"{protocol}{host}:{port}"
    
    return full_url