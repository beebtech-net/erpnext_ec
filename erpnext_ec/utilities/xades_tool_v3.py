import json
import xml.dom.minidom
from types import SimpleNamespace
from lxml import etree
from xml.etree.ElementTree import Element
from lxml.etree import SubElement, _Element
from datetime import datetime
from suds import WebFault
from suds.client import Client
from pprint import pformat
from OpenSSL import crypto
from random import randrange
import frappe
from frappe import _

from cryptography.hazmat.primitives import serialization

from OpenSSL.crypto import FILETYPE_ASN1, FILETYPE_PEM, X509, dump_certificate, load_certificate
from base64 import b64decode, b64encode

from cryptography import x509
from cryptography.hazmat.backends import default_backend

from frappe.utils.password import get_decrypted_password

from xmlsec import SignatureContext, Key, constants, tree

class XadesToolV3():
    def sign_xml(self, xml_string_data, doc, signature_doc):
        def new_range():
            return randrange(100000, 999999)
        
        password_p12 = get_decrypted_password('Sri Signature', signature_doc.name, "password")

        full_path_p12 = frappe.get_site_path() + signature_doc.p12        
        
        with open(full_path_p12, "rb") as f:
            (
                private_key , certificate, additional_certificates
            ) = serialization.pkcs12.load_key_and_certificates(
                f.read() , password_p12.encode(), default_backend()                    
            )

        # Convert the private key to PEM format
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Convert the certificate to PEM format
        certificate_pem = certificate.public_bytes(encoding=serialization.Encoding.PEM)

        #print('private_key_pem')
        #print(private_key_pem)
        #print('certificate_pem')
        #print(certificate_pem)

        #print('XML')
        #print(xml_string_data)

        doc_etree = etree.fromstring(xml_string_data)

        # SIGNATURE STRUCTURE-BEGIN
        signature_id = f"Signature-{new_range()}"
        signature_property_id = f"SignedProperties-{signature_id}"
        certificate_id = f"Certificate-{new_range()}"
        reference_uri = f"Reference-{new_range()}"
        
        signature = etree.Element("{http://www.w3.org/2000/09/xmldsig#}Signature", Id=signature_id)
        signed_info = etree.SubElement(signature, "{http://www.w3.org/2000/09/xmldsig#}SignedInfo")
        canonicalization_method = etree.SubElement(signed_info, "{http://www.w3.org/2000/09/xmldsig#}CanonicalizationMethod", Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315")
        signature_method = etree.SubElement(signed_info, "{http://www.w3.org/2000/09/xmldsig#}SignatureMethod", Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1")
        
        reference = etree.SubElement(signed_info, "{http://www.w3.org/2000/09/xmldsig#}Reference", URI="#comprobante")
        transforms = etree.SubElement(reference, "{http://www.w3.org/2000/09/xmldsig#}Transforms")
        transform = etree.SubElement(transforms, "{http://www.w3.org/2000/09/xmldsig#}Transform", Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature")
        digest_method = etree.SubElement(reference, "{http://www.w3.org/2000/09/xmldsig#}DigestMethod", Algorithm="http://www.w3.org/2000/09/xmldsig#sha1")
        digest_value = etree.SubElement(reference, "{http://www.w3.org/2000/09/xmldsig#}DigestValue")
        
        key_info = etree.SubElement(signature, "{http://www.w3.org/2000/09/xmldsig#}KeyInfo", Id=f"KeyInfoId-{signature_id}")
        x509_data = etree.SubElement(key_info, "{http://www.w3.org/2000/09/xmldsig#}X509Data")
        x509_certificate = etree.SubElement(x509_data, "{http://www.w3.org/2000/09/xmldsig#}X509Certificate")
        x509_certificate.text = certificate_pem.decode('utf-8').replace("-----BEGIN CERTIFICATE-----", "").replace("-----END CERTIFICATE-----", "").replace("\n", "")
        
        object_node = etree.SubElement(signature, "{http://www.w3.org/2000/09/xmldsig#}Object", Id=f"XadesObjectId-{new_range()}")
        qualifying_properties = etree.SubElement(object_node, "{http://uri.etsi.org/01903/v1.3.2#}QualifyingProperties", Id=f"QualifyingProperties-{signature_id}", Target=f"#{signature_id}")
        signed_properties = etree.SubElement(qualifying_properties, "{http://uri.etsi.org/01903/v1.3.2#}SignedProperties", Id=signature_property_id)
        signed_signature_properties = etree.SubElement(signed_properties, "{http://uri.etsi.org/01903/v1.3.2#}SignedSignatureProperties")
        signing_time = etree.SubElement(signed_signature_properties, "{http://uri.etsi.org/01903/v1.3.2#}SigningTime")
        
        signing_certificate = etree.SubElement(signed_signature_properties, "{http://uri.etsi.org/01903/v1.3.2#}SigningCertificate")
        cert = etree.SubElement(signing_certificate, "{http://uri.etsi.org/01903/v1.3.2#}Cert")
        cert_digest = etree.SubElement(cert, "{http://uri.etsi.org/01903/v1.3.2#}CertDigest")
        digest_method_cert = etree.SubElement(cert_digest, "{http://www.w3.org/2000/09/xmldsig#}DigestMethod", Algorithm="http://www.w3.org/2000/09/xmldsig#sha1")
        digest_value_cert = etree.SubElement(cert_digest, "{http://www.w3.org/2000/09/xmldsig#}DigestValue")
        
        issuer_serial = etree.SubElement(cert, "{http://uri.etsi.org/01903/v1.3.2#}IssuerSerial")
        x509_issuer_name = etree.SubElement(issuer_serial, "{http://www.w3.org/2000/09/xmldsig#}X509IssuerName")
        x509_serial_number = etree.SubElement(issuer_serial, "{http://www.w3.org/2000/09/xmldsig#}X509SerialNumber")
        
        signed_data_object_properties = etree.SubElement(signed_properties, "{http://uri.etsi.org/01903/v1.3.2#}SignedDataObjectProperties")
        data_object_format = etree.SubElement(signed_data_object_properties, "{http://uri.etsi.org/01903/v1.3.2#}DataObjectFormat", ObjectReference=f"#{reference_uri}")
        mime_type = etree.SubElement(data_object_format, "{http://uri.etsi.org/01903/v1.3.2#}MimeType")
        encoding = etree.SubElement(data_object_format, "{http://uri.etsi.org/01903/v1.3.2#}Encoding")
        
        # SIGNATURE STRUCTURE-END
        doc_etree.append(signature)
        
        # Sign the XML
        ctx = SignatureContext
        ctx.key = Key.from_memory(private_key_pem, constants.KeyDataFormatPem)
        
        #print(doc_etree)
        
        sign_node = tree.find_node(doc_etree, constants.NodeSignature)
        
        #print(etree.tostring(doc_etree, encoding="utf-8").decode())

        ctx.sign(sign_node)

        try:
            ctx.verify(sign_node)
        except Exception as e:
            raise SystemError(u"Error al momento de verificar la firma: %s" % str(e))

        return etree.tostring(doc_etree, encoding="utf-8").decode()

    def get_sri_signature(self, sri_signature):
        #Se desencripta el password desde frappe para poder usarlo
        
        password_p12 = get_decrypted_password('Sri Signature', sri_signature.name, "password")

        #full_path_p12 = '/opt/bench/frappe-bench/sites/principal/' + sri_signature.p12
        full_path_p12 = frappe.get_site_path() + sri_signature.p12
        
        try:
            with open(full_path_p12, "rb") as f:
                (
                    private_key,
                    p12,
                    additional_certificates,
                ) = serialization.pkcs12.load_key_and_certificates(
                    f.read() , password_p12.encode(), default_backend()                    
                )
                print (private_key , p12, additional_certificates)

                return private_key , p12, additional_certificates
        except Exception as e:
            #print("Error validate_password:" + e)
            print(u"Error validate_password: %s", e)
            return None, None    
        
    def get_sri_signature___(self, sri_signature_object):        
        if(sri_signature_object):
            sri_signature_validated, p12, additional_certificates = self.validate_password(self, sri_signature_object)            
            return sri_signature_validated, p12, additional_certificates
    

    def _clean_str(self, string_to_reeplace, list_characters=None):
        """
        Reemplaza caracteres por otros caracteres especificados en la lista
        @param string_to_reeplace:  string a la cual reemplazar caracteres
        @param list_characters:  Lista de tuplas con dos elementos(elemento uno el caracter a reemplazar, elemento dos caracter que reemplazara al elemento uno)
        @return: string con los caracteres reemplazados
        """
        if not string_to_reeplace:
            return string_to_reeplace
        caracters = ['.',',','-','\a','\b','\f','\n','\r','\t','\v']
        for c in caracters:
            string_to_reeplace = string_to_reeplace.replace(c, '')
        if not list_characters:
            list_characters=[(u'á','a'),(u'à','a'),(u'ä','a'),(u'â','a'),(u'Á','A'),(u'À','A'),(u'Ä','A'),(u'Â','A'),
                             (u'é','e'),(u'è','e'),(u'ë','e'),(u'ê','e'),(u'É','E'),(u'È','E'),(u'Ë','E'),(u'Ê','E'),
                             (u'í','i'),(u'ì','i'),(u'ï','i'),(u'î','i'),(u'Í','I'),(u'Ì','I'),(u'Ï','I'),(u'Î','I'),
                             (u'ó','o'),(u'ò','o'),(u'ö','o'),(u'ô','o'),(u'Ó','O'),(u'Ò','O'),(u'Ö','O'),(u'Ô','O'),
                             (u'ú','u'),(u'ù','u'),(u'ü','u'),(u'û','u'),(u'Ú','U'),(u'Ù','U'),(u'Ü','U'),(u'Û','U'),
                             (u'ñ','n'),(u'Ñ','N'),(u'/','-'), (u'&','Y'),(u'º',''), (u'´', '')]
        for character in list_characters:
            string_to_reeplace = string_to_reeplace.replace(character[0],character[1])
        SPACE = ' '
        #en range el ultimo numero no es inclusivo asi que agregarle uno mas
        #espacio en blanco
        range_ascii = [32]
        #numeros
        range_ascii += range(48, 57+1)
        #letras mayusculas
        range_ascii += range(65,90+1)
        #letras minusculas
        range_ascii += range(97,122+1)
        for c in string_to_reeplace:
            try:
                codigo_ascii = ord(c)
            except TypeError:
                codigo_ascii = False
            if codigo_ascii:
                #si no esta dentro del rang ascii reemplazar por un espacio
                if codigo_ascii not in range_ascii:
                    string_to_reeplace = string_to_reeplace.replace(c,SPACE)
            #si no tengo codigo ascii, posiblemente dio error en la conversion
            else:
                string_to_reeplace = string_to_reeplace.replace(c,SPACE)
        return ''.join(string_to_reeplace.splitlines())