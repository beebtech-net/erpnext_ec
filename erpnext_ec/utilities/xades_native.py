import frappe
from frappe.utils.password import get_decrypted_password
from sri_xades_signer import sign_xml as sri_sign_xml

class XadesNative:
    def sign_xml(self, xml_string_data, doc, signature_doc):
        # 1. Determinar qué documento usar para obtener el p12 y la contraseña
        target_doc = signature_doc if signature_doc else doc
        
        # 2. Obtener la contraseña descifrada
        password_p12 = get_decrypted_password('Sri Signature', target_doc.name, "password")
        
        # 3. Construir la ruta absoluta del archivo .p12
        full_path_p12 = frappe.get_site_path() + target_doc.p12
        
        # 4. Llamar directamente a sri_xades_signer
        #    read_file=True indica que pkcs12_file es una ruta de archivo, no contenido binario
        signed_xml = sri_sign_xml(
            pkcs12_file=full_path_p12,
            password=password_p12,
            xml=xml_string_data,
            read_file=True
        )
        
        return signed_xml