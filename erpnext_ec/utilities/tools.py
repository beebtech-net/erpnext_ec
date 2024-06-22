import frappe

@frappe.whitelist()
def get_full_url():
    # Obtener la URL base del sitio
    base_url = frappe.utils.get_url()
    
    # Obtener el host del sitio actual
    current_site = frappe.local.site
    
    # Verificar si está en modo DNS multitenancy
    if frappe.local.conf.get('dns_multitenant'):
        host = current_site
    else:
        # Si no está en modo DNS multitenancy, usar el host de la URL base
        host = base_url
    
    # Verificar el protocolo
    if "https://" in base_url:
        protocol = "https://"
    else:
        protocol = "http://"
    
    # Obtener el puerto configurado o usar un puerto por defecto
    port = frappe.conf.webserver_port if hasattr(frappe.conf, 'webserver_port') else 80
    
    # Construir la URL completa
    if ":" in host:
        # Si el host ya tiene un puerto, no agregar otro
        full_url = f"{protocol}{host}"
    else:
        full_url = f"{protocol}{host}:{port}"
    
    return full_url
