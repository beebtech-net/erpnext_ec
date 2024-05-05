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

#from cryptography import x509
from cryptography.hazmat.backends import default_backend
from erpnext_ec.utilities.xadessri import sign_xml as sign_xml_xs

from requests import Session
import base64

import subprocess
import os

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
        
    def validate_password_old(self, sri_signature):
        #Se desencripta el password desde frappe para poder usarlo
        from frappe.utils.password import get_decrypted_password
        password_p12 = get_decrypted_password('Sri Signature', sri_signature.name, "password")

        #print(password_p12)
        
        #full_path_p12 = '/opt/bench/frappe-bench/sites/principal/' + sri_signature.p12
        full_path_p12 = frappe.get_site_path() + sri_signature.p12
        
        try:
            with open(full_path_p12, "rb") as f:
                p12 = f.read()                
                return p12
            
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
        
        #print(sri_signatures)

        if(sri_signatures):

            sri_signature_object = sri_signatures[0]
            #sri_signature_validated = self.validate_password_old(self, sri_signature_object)
            sri_signature_validated, p12 = self.validate_password(self, sri_signature_object)
            
            return sri_signature_validated, p12
        
    def get_sri_signature_for_old(self, doc):
        #print(doc)

        #doc_object_build = json.loads(doc, object_hook=lambda d: SimpleNamespace(**d))
        
        sri_signatures = frappe.get_all('Sri Signature', fields='*', filters={'name': doc.name})
        
        print(sri_signatures)

        if(sri_signatures):

            sri_signature_object = sri_signatures[0]
            #sri_signature_validated = self.validate_password_old(self, sri_signature_object)
            p12 = self.validate_password_old(self, sri_signature_object)
            
            return p12
    
    def sign_xml_cmd(self, xml_string_data, signature_doc):
        
        tmp_xml = 'ACC-SINV-2024-00024.xml'
        p12 = 'beebtech_0919826958001.p12'
        password = 'beebtech2022CB'
        output_xml = 'ACC-SINV-2024-00024_signed.xml'

        dir_path = os.path.dirname(os.path.realpath(__file__))

        # Nombre del archivo XSD
        appPath = dir_path + "/apps/XadesSignerCmd/XadesSignerCmd"
        tmpFolder = dir_path + "/apps/XadesSignerCmd/" 

        p = subprocess.Popen([appPath,
                              '--fileinput', tmpFolder + tmp_xml ,
                              '--p12', tmpFolder + p12,
                              '--password', password,
                              '--output', tmpFolder + output_xml])

        res = p.communicate()

        #Leer XML Firmado

        return ""

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
        #return etree.tostring(doc_etree, encoding="utf-8", pretty_print=True).decode()
        #return etree.tostring(doc_etree, encoding="utf-8", xml_declaration=True).decode()
        return etree.tostring(doc_etree, encoding="utf-8").decode()

    def sign_xml_old(self, xml_string_data, signature_doc):
        
        doc_object_build = json.loads(signature_doc, object_hook=lambda d: SimpleNamespace(**d))

        sri_signatures = frappe.get_all('Sri Signature', fields='*', filters={'name': doc_object_build.name})
        
        #print(sri_signatures)        
        
        if(sri_signatures):
            sri_signature_object = sri_signatures[0]
            full_path_p12 = frappe.get_site_path() + sri_signature_object.p12
            #print(full_path_p12)
            with open(full_path_p12, 'rb') as f:
                p12 = f.read()
                #print(pfx_data)

        password = "beebtech2022CB".encode()
        print(type(xml_string_data))
        print("---------------------------------------------------")
        signed = sign_xml_xs(p12, password, xml_string_data)

        #print("signed: ", signed)
        return signed

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
