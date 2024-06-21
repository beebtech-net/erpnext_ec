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

from signxml import XMLSigner, XMLVerifier, methods

from cryptography.hazmat.primitives import serialization

from signxml import DigestAlgorithm
from signxml.xades import (XAdESSigner, XAdESVerifier, XAdESVerifyResult,
                           XAdESSignaturePolicy, XAdESDataObjectFormat, 
                           XAdESSignatureConfiguration)

from OpenSSL.crypto import FILETYPE_ASN1, FILETYPE_PEM, X509, dump_certificate, load_certificate
from base64 import b64decode, b64encode

from cryptography import x509
from cryptography.hazmat.backends import default_backend

from frappe.utils.password import get_decrypted_password

from signxml.util import SigningSettings, add_pem_header, ds_tag, namespaces, xades_tag
from typing import Dict, List, Optional, Union

from signxml.algorithms import (
    CanonicalizationMethod,
    DigestAlgorithm,
    SignatureConstructionMethod,
    SignatureMethod,
    digest_algorithm_implementations,
)

class MyXAdESSigner(XAdESSigner):
    def add_signing_certificate(self, signed_signature_properties, sig_root, signing_settings: SigningSettings):
        # TODO: check if we need to support SigningCertificate
        signing_cert_v2 = SubElement(
            signed_signature_properties, xades_tag("SigningCertificate"), nsmap=self.namespaces
        )
        for cert in signing_settings.cert_chain:  # type: ignore
            if isinstance(cert, X509):
                loaded_cert = cert
            else:
                loaded_cert = load_certificate(FILETYPE_PEM, add_pem_header(cert))
            der_encoded_cert = dump_certificate(FILETYPE_ASN1, loaded_cert)
            cert_digest_bytes = self._get_digest(der_encoded_cert, algorithm=self.digest_alg)
            cert_node = SubElement(signing_cert_v2, xades_tag("Cert"), nsmap=self.namespaces)
            cert_digest = SubElement(cert_node, xades_tag("CertDigest"), nsmap=self.namespaces)
            SubElement(cert_digest, ds_tag("DigestMethod"), nsmap=self.namespaces, Algorithm=self.digest_alg.value)
            digest_value_node = SubElement(cert_digest, ds_tag("DigestValue"), nsmap=self.namespaces)
            digest_value_node.text = b64encode(cert_digest_bytes).decode()
          
            issuer = loaded_cert.get_issuer()
            serial_number = loaded_cert.get_serial_number()
                    
            # Construir el nombre completo del emisor
            issuer_cn = issuer.commonName if issuer.commonName else ''
            issuer_o = issuer.organizationName if issuer.organizationName else ''
            issuer_ou = issuer.organizationalUnitName if issuer.organizationalUnitName else ''
            issuer_c = issuer.countryName if issuer.countryName else ''

            issuer_full_name = f"CN={issuer_cn}, OU={issuer_ou}, O={issuer_o}, C={issuer_c}"
            # subject = loaded_cert.get_subject()
            # common_name = subject.CN
            # organization = subject.O
            # country_name = subject.C

            # print(f"Common Name (CN): {common_name}")
            # print(f"Organization (O): {organization}")
            # print(f"Country Name (C): {country_name}")
            
            issuer_serial = SubElement(cert_node, xades_tag("IssuerSerial"), nsmap=self.namespaces)
            issuer_name_node = SubElement(issuer_serial, ds_tag("X509IssuerName"), nsmap=self.namespaces)
            issuer_name_node.text = issuer_full_name

            issuer_serial_number_node = SubElement(issuer_serial, ds_tag("X509SerialNumber"), nsmap=self.namespaces)
            issuer_serial_number_node.text = str(serial_number)

    
    def __init__(
        self,
        signature_policy: Optional[XAdESSignaturePolicy] = None,
        claimed_roles: Optional[List] = None,
        data_object_format: Optional[XAdESDataObjectFormat] = None,
        **xml_signer_args,
     ) -> None:
        super().__init__(**xml_signer_args)
        if self.sign_alg.name.startswith("HMAC_"):
            raise Exception("HMAC signatures are not supported by XAdES")
        self.signature_annotators.append(self._build_xades_ds_object)
        self._tokens_used: Dict[str, bool] = {}
        self.signed_signature_properties_annotators = [
            self.add_signing_time,
            self.add_signing_certificate,
            self.add_signature_policy_identifier,
            self.add_signature_production_place,
            self.add_signer_role,
        ]
        self.signed_data_object_properties_annotators = [
            self.add_data_object_format,
            self.add_issuer_object
        ]
        self.signature_policy = signature_policy
        self.claimed_roles = claimed_roles
        if data_object_format is None:
            data_object_format = XAdESDataObjectFormat()
        self.data_object_format = data_object_format
        #self.namespaces.update(xades=namespaces.xades)
    
class XadesToolV2():
    def sign_xml(self, xml_string_data, doc, signature_doc):

        password_p12 = get_decrypted_password('Sri Signature', signature_doc.name, "password")

        full_path_p12 = frappe.get_site_path() + signature_doc.p12        
        
        with open(full_path_p12, "rb") as f:
            (
                private_key , certificate, additional_certificates
            ) = serialization.pkcs12.load_key_and_certificates(
                f.read() , password_p12.encode(), default_backend()                    
            )
        
        #print (private_key , certificate, additional_certificates)

        signature_policy = XAdESSignaturePolicy(
            Identifier="",
            Description="",
            DigestMethod=DigestAlgorithm.SHA256,
            DigestValue="Ohixl6upD6av8N7pEvDABhEL6hM=",
        )
        data_object_format = XAdESDataObjectFormat(
            Description="",
            MimeType="text/xml",
        )
        signer = MyXAdESSigner(
            signature_policy=signature_policy,
            claimed_roles=["signer"],
            data_object_format=data_object_format,
            c14n_algorithm=CanonicalizationMethod.CANONICAL_XML_1_0, #"http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
            method = methods.enveloped,
            signature_algorithm = SignatureMethod.DSA_SHA256,
            digest_algorithm = DigestAlgorithm.SHA256
        )

        #print(signer.signed_signature_properties_annotators)

        doc_etree = etree.fromstring(xml_string_data)
        #x509._from_raw_x509_ptr(certificate)
        certificate_pem = certificate.public_bytes(
            encoding=serialization.Encoding.PEM
        )

        certificate_x509 = x509.load_pem_x509_certificate(certificate_pem, default_backend())
        #issuer_name = certificate_x509.issuer.rfc4514_string()
        #serial_number = certificate_x509.serial_number
        #print(issuer_name)

        # Convertir la clave privada y el certificado a PEM
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Crear la configuración de la firma XAdES
        #xades_signature_config = XAdESSignatureConfiguration(
        #    signature_policy=signature_policy,
        #    claimed_roles=["signer"],
        #    data_object_format=data_object_format,
        #    c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
        #    include_certificate_chain=True,
        #    signing_time="2023-06-17T00:00:00Z",
        #)

        ###########################################
        # Ahora añadimos manualmente el elemento <xades:Cert> con la información del emisor y número de serie
        #qualifying_properties = etree.Element("{http://uri.etsi.org/01903/v1.3.2#}QualifyingProperties")
        #signed_properties = etree.SubElement(qualifying_properties, "{http://uri.etsi.org/01903/v1.3.2#}SignedProperties")
        #signed_signature_properties = etree.SubElement(signed_properties, "{http://uri.etsi.org/01903/v1.3.2#}SignedSignatureProperties")

        #signing_certificate = etree.SubElement(signed_signature_properties, "{http://uri.etsi.org/01903/v1.3.2#}SigningCertificate")
        #cert = etree.SubElement(signing_certificate, "{http://uri.etsi.org/01903/v1.3.2#}Cert")
        #issuer_serial = etree.SubElement(cert, "{http://uri.etsi.org/01903/v1.3.2#}IssuerSerial")
        #x509_issuer_name = etree.SubElement(issuer_serial, "{http://www.w3.org/2000/09/xmldsig#}X509IssuerName")
        #x509_issuer_name.text = issuer_name
        #x509_serial_number = etree.SubElement(issuer_serial, "{http://www.w3.org/2000/09/xmldsig#}X509SerialNumber")
        #x509_serial_number.text = str(serial_number)

        #doc_etree.append(qualifying_properties)
        #############################################
                
        signed_xml = signer.sign(
            data=doc_etree,
            key=private_key_pem,
            cert=certificate_pem,
            always_add_key_value=True
            #cert_chain=[cert.public_bytes(encoding=serialization.Encoding.PEM) for cert in additional_certificates]
        )

        #signed_doc = signer.sign(doc_etree, 
        #                         key=private_key_pem, 
        #                         cert=[certificate_x509.public_bytes(serialization.Encoding.DER)])
        certificates = [certificate] + additional_certificates
        additional_certs_pem = [cert.public_bytes(encoding=serialization.Encoding.PEM) for cert in additional_certificates]

        #print (signed_xml)
        try:
            verifier = XAdESVerifier()
            verify_results = verifier.verify(
                signed_xml, 
                x509_cert=certificate_pem,
                require_x509=True
            )
            print("Signature is valid")
        except Exception as e:
            print(f"Signature verification failed: {e}")
        
        #xml_str = etree.tostring(signed_xml, encoding="utf-8", pretty_print=True).decode()
        #xml_beautified = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ", newl="")
        #return xml_beautified
    
        return etree.tostring(signed_xml, encoding="utf-8").decode()

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