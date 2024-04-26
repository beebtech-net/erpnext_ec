import json
from types import SimpleNamespace
from lxml import etree
from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import datetime
from suds import WebFault
from suds.client import Client
from pprint import pformat
from OpenSSL import crypto
from random import randrange
import xmlsig
from xades import template,XAdESContext
from xades.policy import GenericPolicyId, ImpliedPolicy
import frappe
from frappe import _

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
#from cryptography.hazmat.backends import default_backend
#from cryptography.hazmat.primitives.serialization import load_pkcs12
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from cryptography import x509 as x509_crypt
from requests import Session

class SriXmlData():
    
    def validate_password(self, sri_signature):
        #Se desencripta el password desde frappe para poder usarlo
        from frappe.utils.password import get_decrypted_password
        password_p12 = get_decrypted_password('Sri Signature', sri_signature.name, "password")

        #print(password_p12)

        #print(sri_signature.password)
        #password_p12 = 'beebtech2022CB'
        #password_p12 = sri_signature.password
        
        #full_path_p12 = '/opt/bench/frappe-bench/sites/principal/' + sri_signature.p12
        full_path_p12 = frappe.get_site_path() + sri_signature.p12
        
        try:
            with open(full_path_p12, "rb") as f:
                (
                    private_key,
                    p12,
                    additional_certificates,
                ) = serialization.pkcs12.load_key_and_certificates(
                    f.read() , password_p12.encode()
                    #, CLIENT_CERT_KEY.encode()
                )                
                return private_key , p12
        except Exception as e:
            #print("Error validate_password:" + e)
            print(u"Error validate_password: %s", e)
            return None, None    

    def get_sri_signature(self, doc):
        #print(doc)

        doc_object_build = json.loads(doc, object_hook=lambda d: SimpleNamespace(**d))
        
        #print(doc_object_build.name)

        #sri_signature = frappe.get_all('Sri Environment', fields='*', filters={'name': doc.sri_active_environment})        
        sri_signatures = frappe.get_all('Sri Signature', fields='*', filters={'name': doc_object_build.name})
        
        print(sri_signatures)

        if(sri_signatures):

            sri_signature_object = sri_signatures[0]
            #sri_signature_validated = self.validate_password_old(self, sri_signature_object)
            sri_signature_validated, p12 = self.validate_password(self, sri_signature_object)
            
            return sri_signature_validated, p12
    

    def sign_xml(self, xml_string_data, doc, signature_doc):
        def new_range():
            return randrange(100000, 999999)
        
        #digital_signature = self.get_sri_signature(doc)
        private_key , p12 = self.get_sri_signature(self, signature_doc)
        
        if(private_key is None and p12 is None):
            print("P12 o password erroneos")
            return None
        #print(private_key)

        doc_etree = etree.fromstring(xml_string_data)

        #SIGNATURE STRUCTURE-BEGIN
        signature_id = f"Signature{new_range()}"
        signature_property_id = f"{signature_id}-SignedPropertiesID{new_range()}"
        certificate_id = f"Certificate{new_range()}"
        reference_uri = f"Reference-ID-{new_range()}"
        signature = xmlsig.template.create(
            xmlsig.constants.TransformInclC14N,
            xmlsig.constants.TransformRsaSha1,
            signature_id,
        )
        xmlsig.template.add_reference(
            signature,
            xmlsig.constants.TransformSha1,
            name=f"SignedPropertiesID{new_range()}",
            uri=f"#{signature_property_id}",
            uri_type="http://uri.etsi.org/01903#SignedProperties",
        )
        xmlsig.template.add_reference(signature, xmlsig.constants.TransformSha1, uri=f"#{certificate_id}")
        ref = xmlsig.template.add_reference(
            signature,
            xmlsig.constants.TransformSha1,
            name=reference_uri,
            #uri="#comprobante",
        )
        xmlsig.template.add_transform(ref, xmlsig.constants.TransformEnveloped)
        ki = xmlsig.template.ensure_key_info(signature, name=certificate_id)
        data = xmlsig.template.add_x509_data(ki)
        xmlsig.template.x509_data_add_certificate(data)
        xmlsig.template.add_key_value(ki)
        qualifying = template.create_qualifying_properties(signature, name=signature_id)
        props = template.create_signed_properties(qualifying, name=signature_property_id)
        signed_do = template.ensure_signed_data_object_properties(props)
        template.add_data_object_format(
            signed_do,
            f"#{reference_uri}",
            description="contenido comprobante",
            mime_type="text/xml",
        )
        #SIGNATURE STRUCTURE-END

        doc_etree.append(signature)
        is_digital_signature = False
        x509 = None
        # revisar si el certificado tiene la extension digital_signature activada
        # caso contrario tomar del listado de certificados el primero que tengan esta extension
        # x509_to_review = p12.get_certificate().to_cryptography()
        
        x509_to_review = p12
        #print(x509_to_review)
        for exten in x509_to_review.extensions:
            #print(exten)
            if exten.oid._name == "keyUsage" and exten.value.digital_signature:
                is_digital_signature = True
                break

        ctx = XAdESContext(ImpliedPolicy(xmlsig.constants.TransformSha1), certificates=[p12])
        
        certificado_pem = p12.public_bytes(encoding=serialization.Encoding.PEM)

        #print(certificado_pem)

        certificado_x509 = x509_crypt.load_pem_x509_certificate(certificado_pem)
        ctx.private_key = private_key
        ctx.x509 = certificado_x509

        #print(ctx.x509)
        #ctx.load_pkcs12(p12)        
        #print("ctx-----------------------------")
        #print(ctx)
        
        ctx.sign(signature)

        try:
            ctx.verify(signature)
        except Exception as e:
            #error = self._clean_str(tools.ustr(e))
            #_logger.warning(u"Error al momento de verificar la firma: %s", error)
            raise SystemError(u"Error al momento de verificar la firma: %s", e)

        #Devuelve el XML en cadena de string
        return etree.tostring(doc_etree, encoding="UTF-8", pretty_print=True).decode()
