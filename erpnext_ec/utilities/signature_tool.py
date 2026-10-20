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
from xades import template, XAdESContext
from xades.policy import GenericPolicyId, ImpliedPolicy
import frappe
from frappe import _

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from cryptography import x509 as x509_crypt
from cryptography.hazmat.backends import default_backend

from requests import Session
import base64

import subprocess
import os
import uuid

from erpnext_ec.utilities.secure_reader import (
    read_file_in_site,
    write_file_in_site,
    remove_file_in_site,
)


class SriXmlData():

    def validate_password(self, sri_signature):
        # Se desencripta el password desde frappe para poder usarlo
        from frappe.utils.password import get_decrypted_password
        password_p12 = get_decrypted_password('Sri Signature', sri_signature.name, "password")

        try:
            # full_path_p12 = '/opt/bench/frappe-bench/sites/principal/' + sri_signature.p12
            # full_path_p12 = frappe.get_site_path() + sri_signature.p12
            p12_bytes = read_file_in_site(sri_signature.p12, mode="rb")

            (
                private_key,
                p12,
                additional_certificates,
            ) = serialization.pkcs12.load_key_and_certificates(
                p12_bytes, password_p12.encode()
            )
            return private_key, p12
        except Exception as e:
            frappe.logger().error("Error validate_password: %s" % e)
            return None, None

    def validate_password_old(self, sri_signature):
        # Se desencripta el password desde frappe para poder usarlo
        from frappe.utils.password import get_decrypted_password
        password_p12 = get_decrypted_password('Sri Signature', sri_signature.name, "password")

        try:
            # full_path_p12 = frappe.get_site_path() + sri_signature.p12
            p12 = read_file_in_site(sri_signature.p12, mode="rb")
            return p12

        except Exception as e:
            frappe.logger().error("Error validate_password: %s" % e)
            return None, None

    def get_sri_signature(self, sri_signature_object):
        if sri_signature_object:
            sri_signature_validated, p12 = self.validate_password(self, sri_signature_object)
            return sri_signature_validated, p12

    def get_sri_signature_from_json(self, doc):
        doc_object_build = json.loads(doc, object_hook=lambda d: SimpleNamespace(**d))

        sri_signatures = frappe.get_all(
            'Sri Signature', fields='*', filters={'name': doc_object_build.name}
        )

        if sri_signatures:
            sri_signature_object = sri_signatures[0]
            sri_signature_validated, p12 = self.validate_password(self, sri_signature_object)
            return sri_signature_validated, p12

    def get_sri_signature_for_old(self, doc):
        sri_signatures = frappe.get_all(
            'Sri Signature', fields='*', filters={'name': doc.name}
        )
        frappe.logger().info(sri_signatures)

        if sri_signatures:
            sri_signature_object = sri_signatures[0]
            p12 = self.validate_password_old(self, sri_signature_object)
            return p12

    def sign_xml_cmd(self, xml_string_data, signature_doc):
        nombre_temporal = str(uuid.uuid4())

        tmp_xml_rel = f'/private/files/{nombre_temporal}.xml'
        output_xml_rel = f'/private/files/{nombre_temporal}_signed.xml'

        tmp_xml = frappe.get_site_path() + tmp_xml_rel
        output_xml = frappe.get_site_path() + output_xml_rel

        # Escritura segura del XML temporal
        write_file_in_site(tmp_xml_rel, xml_string_data, mode="w")

        p12 = frappe.get_site_path() + signature_doc.p12
        from frappe.utils.password import get_decrypted_password
        password = get_decrypted_password('Sri Signature', signature_doc.name, "password")

        dir_path = os.path.dirname(os.path.realpath(__file__))

        # Nombre del archivo XSD
        appPath = dir_path + "/apps/XadesSignerCmd/XadesSignerCmd"
        tmpFolder = dir_path + "/apps/XadesSignerCmd/"

        p = subprocess.Popen([appPath,
                              '--fileinput', tmp_xml,
                              '--p12', p12,
                              '--password', password,
                              '--output', output_xml])

        res = p.communicate()

        # Leer XML Firmado de forma segura
        content = read_file_in_site(output_xml_rel, mode="r")

        # En caso de usar firmas UANATACA
        # content = content.replace('organizationIdentifier=VATES-A66721499', '2.5.4.97=#0c0f56415445532d413636373231343939')

        try:
            remove_file_in_site(tmp_xml_rel)
            remove_file_in_site(output_xml_rel)
        except FileNotFoundError:
            pass
        except Exception as e:
            frappe.logger().error("Error eliminando archivos temporales: %s" % e)

        return content

    def _clean_str(self, string_to_reeplace, list_characters=None):
        """
        Reemplaza caracteres por otros caracteres especificados en la lista
        @param string_to_reeplace:  string a la cual reemplazar caracteres
        @param list_characters:  Lista de tuplas con dos elementos(elemento uno el caracter a reemplazar, elemento dos caracter que reemplazara al elemento uno)
        @return: string con los caracteres reemplazados
        """
        if not string_to_reeplace:
            return string_to_reeplace
        caracters = ['.', ',', '-', '\a', '\b', '\f', '\n', '\r', '\t', '\v']
        for c in caracters:
            string_to_reeplace = string_to_reeplace.replace(c, '')
        if not list_characters:
            list_characters = [
                (u'á', 'a'), (u'à', 'a'), (u'ä', 'a'), (u'â', 'a'), (u'Á', 'A'), (u'À', 'A'), (u'Ä', 'A'), (u'Â', 'A'),
                (u'é', 'e'), (u'è', 'e'), (u'ë', 'e'), (u'ê', 'e'), (u'É', 'E'), (u'È', 'E'), (u'Ë', 'E'), (u'Ê', 'E'),
                (u'í', 'i'), (u'ì', 'i'), (u'ï', 'i'), (u'î', 'i'), (u'Í', 'I'), (u'Ì', 'I'), (u'Ï', 'I'), (u'Î', 'I'),
                (u'ó', 'o'), (u'ò', 'o'), (u'ö', 'o'), (u'ô', 'o'), (u'Ó', 'O'), (u'Ò', 'O'), (u'Ö', 'O'), (u'Ô', 'O'),
                (u'ú', 'u'), (u'ù', 'u'), (u'ü', 'u'), (u'û', 'u'), (u'Ú', 'U'), (u'Ù', 'U'), (u'Ü', 'U'), (u'Û', 'U'),
                (u'ñ', 'n'), (u'Ñ', 'N'), (u'/', '-'), (u'&', 'Y'), (u'º', ''), (u'´', '')
            ]
        for character in list_characters:
            string_to_reeplace = string_to_reeplace.replace(character[0], character[1])
        SPACE = ' '
        range_ascii = [32]
        range_ascii += range(48, 57 + 1)
        range_ascii += range(65, 90 + 1)
        range_ascii += range(97, 122 + 1)
        for c in string_to_reeplace:
            try:
                codigo_ascii = ord(c)
            except TypeError:
                codigo_ascii = False
            if codigo_ascii:
                if codigo_ascii not in range_ascii:
                    string_to_reeplace = string_to_reeplace.replace(c, SPACE)
            else:
                string_to_reeplace = string_to_reeplace.replace(c, SPACE)
        return ''.join(string_to_reeplace.splitlines())