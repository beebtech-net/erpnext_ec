import os
import time
import logging
import traceback

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
import base64
import tempfile
import subprocess
import frappe
from frappe import _

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
#from cryptography.hazmat.primitives.serialization import load_pkcs12
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from cryptography import x509 as x509_crypt
from requests import Session

KEY_TO_PEM_CMD = "openssl pkcs12 -nocerts -in %s -out %s -passin pass:%s -passout pass:%s"

STATES = {
        "unverified": [
            ("readonly", False),
        ]
    }

class SriXmlData():

    def convert_key_cer_to_pem(self, key, password):
        # TODO compute it from a python way
        with tempfile.NamedTemporaryFile(
                "wb", suffix=".key", prefix="edi.ec.tmp.", delete=False
        ) as key_file, tempfile.NamedTemporaryFile("rb", suffix=".key", prefix="edi.ec.tmp.",delete=False) as keypem_file:
            key_file.write(key)
            key_file.flush()
            subprocess.call((KEY_TO_PEM_CMD % (key_file.name, keypem_file.name, password, password)).split())
            key_pem = keypem_file.read().decode()
        return key_pem
    

    def validate_password___(self, sri_signature):       
        password_p12 = "Mnsa2023"

        full_path_p12 = '/opt/bench/frappe-bench/sites/principal/private/files/macro_until_25092026.p12'

        private_key_str = """
-----BEGIN ENCRYPTED PRIVATE KEY-----
MIIFHDBOBgkqhkiG9w0BBQ0wQTApBgkqhkiG9w0BBQwwHAQIdFBnb6QxuP8CAggA
MAwGCCqGSIb3DQIJBQAwFAYIKoZIhvcNAwcECC/qKsbnlFtwBIIEyLLIciZkrA24
miB1qfPJRflDCXnRUwWE/k8Tl6U/mgW0CRUt06WiWkncGu1VGFbGTzRQRPR+bQwP
mbpLft6ulnTNDqAZppGwrXRs1ZaSo5SLguq/fxjQUiVMlKP9pIJRDaRz6i2GE91r
e/ni9vJRDnDyYPGibTTRcLYjx4DzdTLM6XaL/8Fp9C3LpjViL0NeYp8V3camyiBL
df5hXsPPPUAhs4FIVg6JY0tklMgRwjEA4xY8p6VWZ9TonlYn3x7eUoio6FMMLLw0
d2sNAKZqePY2YLhDn2BZH8lR8+X6x0ajW2tpKFdMLBR9qpq2/zZjbaivL7BrSy61
qsiAR2T7GgVRtypGwQNbrNHvJ7tG9i4Ao2tQeSpTOcEG/xwVKSnKjxkgnF2ni/Xg
0FXaf2PSsFbSiofSRMNGEUvw1otwYP3JdlA/ql1hdQdNRbibpHX8dwUmwDggbeCL
jIlebDX+LAMzc/+rgHRUR0/WHmmhzNDAHcSMXd2iaJntyMK7UyVKxIVk47Jznmtq
TIuS4yIGMPknrHwXtr6XoFl6mCy1URbIEqJDIb2bgMgw4BbJrwR3kMTAgM74Tb1f
jBwiRF4JAi2BinkoeCB+8FVNHSh2tA/PD0UGpqdCrUUvIw3L4uYvDzEPYQr/MHb6
91frQjUTT5Yhn43gJ4cB3EXeCxY2lRNrFQ48X+MtMTjDD6L3rohrE4sZfX3Y6S7h
eK9ugISPKOOAc0RgMFtrgwhiR6m5uCFP2t+AkZtYI2dSFX0aTMh6dz294R4GIwmr
QASPf12bpGjd1t2uGUXKTVGTtVw884oyAjFqgrOsZcJe5q8NYJQCaO51aORHatwf
BPu0/ryv6Sws2vtAoJDIVrOKPuB/YkInNA+BUvhxjy8/3FuIB0o5v2e+CZUDS3ZI
mEjPX0Z/Z9dQXYxWSpJ3oRMRQ5GSG3r47OBwaPOjM0nw1zOuB1z6UMgKdQ9PdDuu
ZrzQ4nRXT0Aui5Il0gSCIm7zZtYkq04cipbmZ/I/r8XcXD95TvSn5IF5hGtwr3LY
2QHsjLOC7vEnRpS4jZvIYQ/JMEXyhU9rV9pKaYoFSwMYA/fW8E+TdihEiTjd1I90
F8YL+1jS8isZeH4xypmovR0xwIsLsq/LediGErIiGyKPdli92kjyCtyG2CrRSUqs
0kjNzYY7CmBeG8csjuVujX8S3oEvAoF/MVBHpUbEfXUuK17a1WeGjsC++SbrtSeQ
WoA4r0K/YeqqSFQlpHdUvRCqGoXRrKkEFcneWCRq5vcaDmKMQIfl1FcenAw3DTPy
KJJXQqM9WwuBU5l/MaftJZEgCcv8AbEiyajOtc15gXh0S1V0IRACc+0edG9ba4Kc
ZCwBHDfwyqiXgvN7V7SSZ6oxZxZeqKlZ3fzAOEMmGyaAm62rtYPUuMpMofGhyQzN
MBz4o2m+092WDKkZGlCS50IjleOOSI+mRXRLFzn8aoWDpx2lEAY70WHYAY13GWWT
wdQPVsAX/0KeJYOh602NMPjiJMnWod5eu1glMpn+2pKjO5pxY4wYj3wdIc6lyLOr
rRHJDQcnqgDqxC/8j8HmeE+bDQJvcnIt6cx+7STG0a7JQpusKShhVpkbL31hSqHM
thGwkHjMrPdTILvEh6AzJw==
-----END ENCRYPTED PRIVATE KEY-----
"""

        try:
            
            file = open(full_path_p12, "rb")
            filecontent = file.read()
            
            file.close()
            
            #base64.b64decode(

            private_key = crypto.load_privatekey(
                crypto.FILETYPE_PEM,
                private_key_str.encode("ascii"), #digital_signature.private_key.encode("ascii"),
                password_p12.encode(),
            )
            
            p12 = crypto.load_pkcs12(filecontent, password_p12.encode())
            
            return private_key, p12
        
        except Exception as ex:
            print("ERROR:")
            print(ex)

    def validate_password(self, sri_signature):
        #Se desencripta el password desde frappe para poder usarlo
        from frappe.utils.password import get_decrypted_password
        password_p12 = get_decrypted_password('Sri Signature', sri_signature.name, "password")

        #print(password_p12)

        #print(sri_signature.password)
        #password_p12 = 'beebtech2022CB'
        #password_p12 = sri_signature.password
        
        full_path_p12 = '/opt/bench/frappe-bench/sites/principal/' + sri_signature.p12
        
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

    def validate_password_v1(self, sri_signature):

        #print(sri_signature.password)
        password_p12 = 'beebtech2022CB'
        
        full_path_p12 = '/opt/bench/frappe-bench/sites/principal/' + sri_signature.p12
        
        # ctx = xmlsig.SignatureContext()
        # print(ctx)
        # with open(full_path_p12, "rb") as key_file:
        #     ctx.load_pkcs12(pkcs12.load_key_and_certificates(key_file.read(), password_p12.encode()))
        #     print("ctx-----------------------------------------------")
        #     print(ctx)
        #     print("ctx-----------------------------------------------FIN")

        with open(full_path_p12, "rb") as f:
            (
            private_key,
            certificate,
            additional_certificates,
        ) = serialization.pkcs12.load_key_and_certificates(
            f.read() , password_p12.encode()
            #, CLIENT_CERT_KEY.encode()
        )
        # key will be available in user readable temporary file for the time of the
        # program run (until key and cert get gc'ed)
        key = tempfile.NamedTemporaryFile(delete=False)
        cert = tempfile.NamedTemporaryFile(delete=False)
        key.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        key.flush()
        cert.write(
            certificate.public_bytes(serialization.Encoding.PEM),
        )
        cert.flush()
        session = Session()
        session.cert = (cert.name, key.name)
                
        return private_key, certificate

    def get_sri_signature(self, doc):
        #print(doc)

        doc_object_build = json.loads(doc, object_hook=lambda d: SimpleNamespace(**d))
        
        #print(doc_object_build.name)

        #sri_signature = frappe.get_all('Sri Environment', fields='*', filters={'name': doc.sri_active_environment})        
        sri_signatures = frappe.get_all('Sri Signature', fields='*', filters={'name': doc_object_build.name})

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
            uri="#comprobante",
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

        # if not is_digital_signature:
        #     # cuando hay mas de un certificado, tomar el certificado correcto
        #     # este deberia tener entre las extensiones digital_signature = True
        #     # pero si el certificado solo tiene uno, devolvera None
        #     ca_certificates_list = p12.get_ca_certificates()
        #     if ca_certificates_list is not None:
        #         for x509_inst in ca_certificates_list:
        #             x509_cryp = x509_inst.to_cryptography()
        #             for exten in x509_cryp.extensions:
        #                 if exten.oid._name == "keyUsage" and exten.value.digital_signature:
        #                     x509 = x509_inst
        #                     break
        # if x509 is not None:
        #     p12.set_certificate(x509)
        #     p12.set_privatekey(private_key)

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

    # def sign_xml_file(self):
    #     if not self.company_id.key_type_id:
    #         #raise UserError("No tiene una firma digital configurada")
    #         raise SystemError("No tiene una firma digital configurada")
    #     digital_signature = self.company_id.key_type_id
    #     if not digital_signature:
    #         #raise UserError("No tiene una firma digital configurada")
    #         raise SystemError("No tiene una firma digital configurada")

    #     document_xml = base64.b64decode(self.xml_report)
    #     xml_string=etree.tostring(etree.fromstring(document_xml),encoding="UTF-8", pretty_print=True).decode()
    #     signed_document=self.sign_xml(xml_string, digital_signature)
    #     self.xml_report = base64.b64encode(signed_document.encode())
    #     self.state='signed'
    #     return signed_document