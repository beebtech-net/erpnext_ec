import os
import time
import logging
import traceback
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
import cryptography.hazmat.primitives.serialization.pkcs12
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

    def validate_password(self, sri_signature):
        #print(sri_signature)
        full_path_p12 = '/opt/bench/frappe-bench/sites/principal/' + sri_signature.p12
        #full_path_p12 = '/opt/bench/frappe-bench/sites/principal/public/files/beebtech_0919826958001.p12'
        
        with open(full_path_p12, 'rb') as f:
            data_p12 = f.read()
            #print(data_p12)
            filecontent = base64.b64decode(data_p12)
            print(filecontent)

        print(sri_signature.password)
        password_p12 = 'beebtech2022CB'

        try:
            p12 = crypto.load_pkcs12(filecontent, bytes(password_p12, 'ascii'))            
        except Exception as ex:
            #_logger.warning(tools.ustr(ex))
            #raise UserError(
            #    _(
            #        "Error opening the signature, possibly the signature key has been entered incorrectly or the file is not supported."
            #    )
            #)

            raise SystemError("Error opening the signature, possibly the signature key has been entered incorrectly or the file is not supported.")
        
        private_key = self.convert_key_cer_to_pem(filecontent, self.password)
        start_index = private_key.find("Signing Key")
        # cuando el archivo tiene mas de una firma electronica
        # viene varias secciones con BEGIN ENCRYPTED PRIVATE KEY
        # diferenciandose por:
        # * Decryption Key
        # * Signing Key
        # asi que tomar desde Signing Key en caso de existir
        if start_index >= 0:
            private_key = private_key[start_index:]
        start_index = private_key.find("-----BEGIN ENCRYPTED PRIVATE KEY-----")
        private_key = private_key[start_index:]
        cert = p12.get_certificate()
        issuer = cert.get_issuer()
        subject = cert.get_subject()
        
        #vals = {
        #    "emision_date": datetime.strptime(cert.get_notBefore().decode("utf-8"), "%Y%m%d%H%M%SZ"),
        #    "expire_date": datetime.strptime(cert.get_notAfter().decode("utf-8"), "%Y%m%d%H%M%SZ"),
        #    "subject_common_name": subject.CN,
        #    "subject_serial_number": subject.serialNumber,
        #    "issuer_common_name": issuer.CN,
        #    "cert_serial_number": cert.get_serial_number(),
        #    "cert_version": cert.get_version(),
        #    "private_key": private_key,
        #    "state": "valid",
        #}
        #self.write(vals)

        data_cert = base64.b64decode(self.electronic_signature)
        cert = tempfile.NamedTemporaryFile(suffix='.p12',delete=False)
        cert.write(data_cert)
        cert.flush()
        try:
            crypto.load_pkcs12(open(cert.name, 'rb').read(), bytes(self.password_signature, 'ascii'))
        except OpenSSL.crypto.Error as e:
            #raise UserError(f"Error al validar, la contrasena es correcta? {e}")
            raise SystemError(f"Error al validar, la contrasena es correcta? {e}")
        return True
    
    def new_mode(self, sri_signature):

        print(sri_signature.password)
        password_p12 = 'beebtech2022CB'

        full_path_p12 = '/opt/bench/frappe-bench/sites/principal/' + sri_signature.p12
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
        return private_key

    def get_sri_signature(self, doc):
        #sri_signature = frappe.get_all('Sri Environment', fields='*', filters={'name': doc.sri_active_environment})        
        sri_signatures = frappe.get_all('Sri Signature', fields='*')

        if(sri_signatures):
            sri_signature_object = sri_signatures[0]
            #sri_signature_validated = self.validate_password(self, sri_signature_object)
            sri_signature_validated = self.new_mode(self, sri_signature_object)
            
            return sri_signature_validated


    def action_sign(self, xml_string_data, doc):
        def new_range():
            return randrange(100000, 999999)

        #digital_signature = self.get_sri_signature(doc)
        digital_signature = self.get_sri_signature(self, doc)
        print(digital_signature)

        # filecontent = base64.b64decode(digital_signature)

        # try:
        #     private_key = crypto.load_privatekey(
        #         crypto.FILETYPE_PEM,
        #         digital_signature.private_key.encode("ascii"),
        #         digital_signature.password_signature.encode(),
        #     )
        #     p12 = crypto.load_pkcs12(filecontent, digital_signature.password_signature)
        # except Exception as ex:
        #     #_logger.warning(tools.ustr(ex))
        #     #raise UserError(
        #     #    _(
        #     #        "Error opening the signature, possibly the signature key has been entered incorrectly or the file is not supported"
        #     #    )
        #     #)
        #     raise SystemError("Error opening the signature, possibly the signature key has been entered incorrectly or the file is not supported")
        
        doc = etree.fromstring(xml_string_data)
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
        doc.append(signature)
        is_digital_signature = False
        x509 = None
        # revisar si el certificado tiene la extension digital_signature activada
        # caso contrario tomar del listado de certificados el primero que tengan esta extension
        x509_to_review = p12.get_certificate().to_cryptography()
        for exten in x509_to_review.extensions:
            if exten.oid._name == "keyUsage" and exten.value.digital_signature:
                is_digital_signature = True
                break
        if not is_digital_signature:
            # cuando hay mas de un certificado, tomar el certificado correcto
            # este deberia tener entre las extensiones digital_signature = True
            # pero si el certificado solo tiene uno, devolvera None
            ca_certificates_list = p12.get_ca_certificates()
            if ca_certificates_list is not None:
                for x509_inst in ca_certificates_list:
                    x509_cryp = x509_inst.to_cryptography()
                    for exten in x509_cryp.extensions:
                        if exten.oid._name == "keyUsage" and exten.value.digital_signature:
                            x509 = x509_inst
                            break
        if x509 is not None:
            p12.set_certificate(x509)
            p12.set_privatekey(private_key)
        ctx = XAdESContext(ImpliedPolicy(xmlsig.constants.TransformSha1))
        ctx.load_pkcs12(p12)
        ctx.sign(signature)
        try:
            ctx.verify(signature)
        except Exception as e:
            #error = self._clean_str(tools.ustr(e))
            #_logger.warning(u"Error al momento de verificar la firma: %s", error)
            raise SystemError(u"Error al momento de verificar la firma: %s", e)

        return etree.tostring(doc, encoding="UTF-8", pretty_print=True).decode()

    def sign_xml_file(self):
        if not self.company_id.key_type_id:
            #raise UserError("No tiene una firma digital configurada")
            raise SystemError("No tiene una firma digital configurada")
        digital_signature = self.company_id.key_type_id
        if not digital_signature:
            #raise UserError("No tiene una firma digital configurada")
            raise SystemError("No tiene una firma digital configurada")

        document_xml = base64.b64decode(self.xml_report)
        xml_string=etree.tostring(etree.fromstring(document_xml),encoding="UTF-8", pretty_print=True).decode()
        signed_document=self.action_sign(xml_string,digital_signature)
        self.xml_report = base64.b64encode(signed_document.encode())
        self.state='signed'
        return signed_document