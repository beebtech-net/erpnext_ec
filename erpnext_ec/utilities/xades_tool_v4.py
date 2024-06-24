from typing import Union, List
import sys
import re
from io import BufferedReader
from datetime import datetime
import base64
import hashlib
from lxml import etree
import xml.etree.ElementTree as ET
import codecs
import random


# crypto
from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography import x509
from cryptography.x509 import Name
from cryptography.x509.oid import NameOID


MAX_LINE_SIZE = 76
XML_NAMESPACES = 'xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:etsi="http://uri.etsi.org/01903/v1.3.2#"'


def random_integer() -> int:
    """
    Generates a random integer between 990 and 999,989 (inclusive).

    Returns:
        int: A random integer.
    """
    return random.randint(990, 999989)

# XML
def format_xml_string(xml_string: str) -> str:
    """
    Format an XML string by removing unnecessary whitespace.

    Args:
        xml_string (str): The XML string to be formatted.

    Returns:
        str: The formatted XML string with unnecessary whitespace removed.
    """
    xml_string = xml_string.replace('\n', '')
    xml_string = re.sub(' +', ' ', xml_string).replace('> ', '>').replace(' <', '<')
    return xml_string


def get_key_info(
    certificate_number: int, 
    certificate_x509: str, 
    modulus: str, 
    exponent: str
) -> str:
    """
    Generate key information XML for a digital certificate.

    Args:
        certificate_number (int): The number of the certificate.
        certificate_x509 (str): The X509 certificate.
        modulus (str): The modulus of the RSA key.
        exponent (str): The exponent of the RSA key.

    Returns:
        str: The key information XML string.
    """
    key_info = f"""
    <ds:KeyInfo Id="Certificate{certificate_number}">
        <ds:X509Data>
            <ds:X509Certificate>
                {certificate_x509}
            </ds:X509Certificate>
        </ds:X509Data>
        <ds:KeyValue>
            <ds:RSAKeyValue>
                <ds:Modulus>
                    {modulus}
                </ds:Modulus>
                <ds:Exponent>{exponent}</ds:Exponent>
            </ds:RSAKeyValue>
        </ds:KeyValue>
    </ds:KeyInfo>
    """

    return key_info


def get_signed_properties(
    signature_number: int, 
    signed_properties_number: int, 
    certificate_x509_der_hash: str, 
    X509SerialNumber: str, 
    reference_id_number: int, 
    issuer_name: str
) -> str:
    signing_time: str = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    signed_properties: str = f"""
    <etsi:SignedProperties Id="Signature{signature_number}-SignedProperties{signed_properties_number}">
        <etsi:SignedSignatureProperties>
            <etsi:SigningTime>
                {signing_time}
            </etsi:SigningTime>
            <etsi:SigningCertificate>
                <etsi:Cert>
                    <etsi:CertDigest>
                        <ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
                        <ds:DigestValue>
                            {certificate_x509_der_hash}
                        </ds:DigestValue>
                    </etsi:CertDigest>
                    <etsi:IssuerSerial>
                        <ds:X509IssuerName>
                            {issuer_name}
                        </ds:X509IssuerName>
                        <ds:X509SerialNumber>
                            {X509SerialNumber}
                        </ds:X509SerialNumber>
                    </etsi:IssuerSerial>
                </etsi:Cert>
            </etsi:SigningCertificate>
        </etsi:SignedSignatureProperties>
        <etsi:SignedDataObjectProperties>
            <etsi:DataObjectFormat ObjectReference="#Reference-ID-{reference_id_number}">
                <etsi:Description>
                    contenido comprobante
                </etsi:Description>
                <etsi:MimeType>
                    text/xml
                </etsi:MimeType>
            </etsi:DataObjectFormat>
        </etsi:SignedDataObjectProperties>
    </etsi:SignedProperties>"""

    properties = format_xml_string(signed_properties)

    return properties


def get_signed_info(
    signed_info_number: int,
    signed_properties_id_number: int,
    sha1_signed_properties: str,
    certificate_number: int,
    sha1_certificado: str,
    reference_id_number: int,
    sha1_comprobante: str,
    signature_number: int,
    signed_properties_number: int
) -> str:
    """
    Generates the SignedInfo element for XML digital signature.

    Args:
        signed_info_number (int): The number for SignedInfo.
        signed_properties_id_number (int): The number for SignedProperties ID.
        sha1_signed_properties (str): The SHA1 hash of the signed properties.
        certificate_number (int): The number for the certificate.
        sha1_certificado (str): The SHA1 hash of the certificate.
        reference_id_number (int): The number for the reference ID.
        sha1_comprobante (str): The SHA1 hash of the document.
        signature_number (int): The number for the signature.
        signed_properties_number (int): The number for SignedProperties.

    Returns:
        str: The SignedInfo XML element.
    """
    signed_info = f"""
        <ds:SignedInfo Id="Signature-SignedInfo{signed_info_number}">
            <ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
            <ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
            <ds:Reference Id="SignedPropertiesID{signed_properties_id_number}" Type="http://uri.etsi.org/01903#SignedProperties" URI="#Signature{signature_number}-SignedProperties{signed_properties_number}">
                <ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
                <ds:DigestValue>{sha1_signed_properties}</ds:DigestValue>
            </ds:Reference>
            <ds:Reference URI="#Certificate{certificate_number}">
                <ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
                <ds:DigestValue>{sha1_certificado}</ds:DigestValue>
            </ds:Reference>
            <ds:Reference Id="Reference-ID-{reference_id_number}" URI="#comprobante">
                <ds:Transforms>
                    <ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
                </ds:Transforms>
                <ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
                <ds:DigestValue>{sha1_comprobante}</ds:DigestValue>
            </ds:Reference>
        </ds:SignedInfo>
    """

    return signed_info


def get_xades_bes(
    xmls: str, 
    signature_number: int, 
    object_number: int, 
    signed_info: str, 
    signature: str, 
    key_info: str, 
    signed_properties: str
) -> str:
    """
    Generate XAdES-BES XML signature.

    Args:
        xmls (str): XML namespace declarations.
        signature_number (int): Number to identify the signature.
        signature_value_number (int): Number to identify the signature value.
        object_number (int): Number to identify the object.
        signed_info (str): Signed information.
        signature (str): Signature value.
        key_info (str): Key information.
        signed_properties (str): Signed properties.

    Returns:
        str: The generated XAdES-BES XML signature string.
    """
    xades_bes = f"""
    <ds:Signature {xmls} Id="Signature{signature_number}">
        {signed_info}
        <ds:SignatureValue>
            {signature}
        </ds:SignatureValue>
        {key_info}
        <ds:Object Id="Signature{signature_number}-Object{object_number}">
            <etsi:QualifyingProperties Target="#Signature{signature_number}">
                {signed_properties}
            </etsi:QualifyingProperties>
        </ds:Object>
    </ds:Signature>
"""

    return xades_bes


# utils
def sha1_base64(text: Union[str, bytes]) -> str:
    """
    Returns the SHA1 hash of the input text encoded in base64.

    Args:
        text (Union[str, bytes]): The input text.

    Returns:
        str: The SHA1 hash encoded in base64.
    """
    m = hashlib.sha1()
    if isinstance(text, str):
        text = text.encode()
    m.update(text)
    sha1_hex = m.digest()
    b64 = encode_base64(sha1_hex)
    return b64


def sha1(text: Union[str, bytes]) -> str:
    """
    Returns the SHA1 hash of the input text.

    Args:
        text (Union[str, bytes]): The input text.

    Returns:
        str: The SHA1 hash.
    """
    m = hashlib.sha1()
    if isinstance(text, str):
        text = text.encode()
    m.update(text)
    return m.hexdigest()


def split_string_every_n(string: str, n: int) -> str:
    """
    Splits a string every n characters.

    Args:
        string (str): The input string.
        n (int): The number of characters to split.

    Returns:
        str: The string with every n characters separated by a newline.
    """
    result = [string[i:i + n] for i in range(0, len(string), n)]
    return '\n'.join(result)


def split_string_by_delimiter(string: str, delimiter: str, append_start: bool = True) -> List[str]:
    """
    Splits a string by a delimiter.

    Args:
        string (str): The input string.
        delimiter (str): The delimiter.
        append_start (bool, optional): Whether to append the delimiter at the start. Defaults to True.

    Returns:
        List[str]: The list of strings split by the delimiter.
    """
    result = string.split(delimiter)
    if append_start:
        return [delimiter + res for res in result]
    else:
        return [res + delimiter for res in result]


def encode_base64(data: Union[str, bytes], encoding: str = 'UTF-8') -> str:
    """
    Encodes a string or bytes to base64.

    Args:
        data (Union[str, bytes]): The input string or bytes.
        encoding (str, optional): The encoding. Defaults to 'UTF-8'.

    Returns:
        str: The base64 encoded string.
    """
    if isinstance(data, str):
        data = data.encode(encoding)
    return base64.b64encode(data).decode(encoding)


def get_xml_end_node(xml_tree: ET.ElementTree) -> str:
    """
    Returns the closing tag for the root node of an XML ElementTree.

    Args:
        xml_tree (ET.ElementTree): The XML ElementTree.

    Returns:
        str: The closing tag for the root node.
    """
    return f"</{xml_tree.getroot().tag}>"


# xades
def canonicalize_lxml(xml_string: Union[str, bytes]) -> str:
    """
    Performs Canonicalization (c14n) on the provided XML string using lxml.

    Args:
        xml_string (str): The XML string to be canonicalized.

    Returns:
        Optional[bytes]: The canonicalized XML as bytes if successful, None otherwise.
    """
    if isinstance(xml_string, bytes):
        xml_string = xml_string.decode('utf-8')

    # Parse the XML string
    root = etree.fromstring(xml_string)

    # Perform canonicalization
    canonical_xml: bytes = etree.tostring(root, method="c14n", exclusive=False, with_comments=False)
    return canonical_xml.decode("utf-8")


def get_exponent(exp_int: int) -> str:
    """
    Converts an integer exponent to a base64 string.

    Args:
        exp_int (int): The integer exponent.

    Returns:
        str: The base64 string representation of the exponent.
    """
    hex_exp = '{:X}'.format(exp_int)
    hex_exp = hex_exp.zfill(6)
    decoded_hex = codecs.decode(hex_exp, 'hex')
    base64_exp = codecs.encode(decoded_hex, 'base64').decode().strip()
    return base64_exp


def get_modulus(modulus_int: int, max_line_size: int = 76) -> str:
    """
    Converts an integer modulus to base64-encoded string and splits it into lines.

    Args:
        modulus_int (int): The integer modulus.
        max_line_size (int): The maximum line size for splitting.

    Returns:
        str: The base64-encoded modulus split into lines.
    """
    # Convert integer modulus to hexadecimal string
    modulus_hex = '{:X}'.format(modulus_int)

    # Divide the hexadecimal string into pairs of characters
    modulus_bytes = bytes.fromhex(modulus_hex)

    # Encode bytes to base64
    modulus_base64 = base64.b64encode(modulus_bytes).decode('latin-1')

    # Split base64-encoded modulus into lines
    modulus_split = '\n'.join([modulus_base64[i:i+max_line_size] for i in range(0, len(modulus_base64), max_line_size)])

    return modulus_split


def get_x509_certificate(certificate_pem: str, max_line_size: int = MAX_LINE_SIZE) -> str:
    """
    Extracts X.509 certificate from PEM-encoded string and splits it into lines.

    Args:
        certificate_pem (str): The PEM-encoded certificate string.
        max_line_size (int): The maximum line size for splitting.

    Returns:
        str: The X.509 certificate split into lines.
    """
    # Find X.509 certificate between "-----BEGIN CERTIFICATE-----" and "-----END CERTIFICATE-----"
    certificate_regex = r"-----BEGIN CERTIFICATE-----(.*?)-----END CERTIFICATE-----"
    certificate_match = re.search(certificate_regex, certificate_pem, flags=re.DOTALL)

    if certificate_match:
        certificate_x509 = certificate_match.group(1)
        certificate_x509 = '\n'.join([certificate_x509[i:i+max_line_size] for i in range(0, len(certificate_x509), max_line_size)])
        return certificate_x509
    else:
        return ''
    

def get_private_key(file: Union[str, bytes, BufferedReader], password: Union[str, bytes], read_file: bool = False):
    """
    Retrieves the private key from a PKCS#12 file.

    Args:
        file (Union[str, bytes, BufferedReader]): The path to the PKCS#12 file,
            or the PKCS#12 file content as bytes, or a BufferedReader object.
        password (Union[str, bytes]): The password to decrypt the PKCS#12 file.
        read_file (bool, optional): If True and `file` is a string representing a file path,
            the function will read the file content. Defaults to False.

    Returns:
        Optional[str]: The private key in PEM format if successful, None otherwise.
    """

    if isinstance(file, str):
        if read_file:
            with open(file, 'rb') as p12_file:
                data = p12_file.read()
        else:
            data = file.encode("utf-8")

    if isinstance(file, bytes):
        data = file
        
    if isinstance(file, BufferedReader):
        data = file.read()
    
    if isinstance(password, str):
        password = password.encode()
    
    keys = pkcs12.load_pkcs12(data, password)

    return keys


def parse_issuer_name(issuer: Name):
    """
    Parses and formats the issuer name from the given X.509 certificate.

    Args:
        issuer (x509.Name): The X.509 issuer name.

    Returns:
        Optional[str]: The formatted issuer name if successful, None otherwise.
    """
    issuer_name = ""
    for attribute in issuer:
        if isinstance(attribute.value, x509.Name):
            for name_attribute in attribute.value:
                if name_attribute.oid == NameOID.COMMON_NAME:
                    issuer_name += f",CN={name_attribute.value}"
                # Add other checks for different fields if needed
    # Remove the leading comma if present
    issuer_name = issuer_name.lstrip(',')
    return issuer_name


def sign_xml(
    pkcs12_file: Union[str, bytes], 
    password: Union[str, bytes], 
    xml: str, 
    read_file: bool = False
) -> str:
    """
    Processes and signs a XML document.

    Args:
        pkcs12_file (Union[str, bytes]): The path to the PKCS12 file or the content of the file.
        password (Union[str, bytes]): The password to decrypt the PKCS12 file.
        xml (str): The XML document to sign.
        read_file (bool, optional): Whether to read the PKCS12 file as a binary file. Defaults to False.

    Returns:
        str: The signed XML document.
    """
    
    if isinstance(password, str):
        password = password.encode("utf-8")

    keys = get_private_key(pkcs12_file, password, read_file=read_file)
    certificate_pem = keys.cert.certificate.public_bytes(encoding=serialization.Encoding.PEM)

    certificate_x509 = get_x509_certificate(certificate_pem.decode("utf-8"))
    certificate_x509_der_hash = sha1_base64(certificate_pem)

    public_key_numbers = keys.cert.certificate.public_key().public_numbers()
    modulus = get_modulus(public_key_numbers.n)
    exponent = get_exponent(public_key_numbers.e)

    serial_number = keys.cert.certificate.serial_number
    issuer_name = parse_issuer_name(keys.cert.certificate.issuer)

    xml_tree = ET.ElementTree(ET.fromstring(xml))
    xml_no_header = canonicalize_lxml(xml)

    sha1_invoice = sha1_base64(xml_no_header.encode())

    certificate_number = random_integer()
    signature_number = random_integer()
    signed_properties_number = random_integer()

    signed_info_number = random_integer()
    signed_properties_id_number = random_integer()
    reference_id_number = random_integer()
    signature_value_number = random_integer()

    signed_properties = get_signed_properties(
        signature_number, 
        signed_properties_number, 
        certificate_x509_der_hash, 
        serial_number,
        reference_id_number, 
        issuer_name
    )

    signed_properties_for_hash = signed_properties.replace('<etsi:SignedProperties', '<etsi:SignedProperties ' + XML_NAMESPACES)
    signed_properties_for_hash = canonicalize_lxml(signed_properties_for_hash)

    sha1_signed_properties = sha1_base64(signed_properties_for_hash.encode())

    key_info = get_key_info(
        certificate_number, 
        certificate_x509, 
        modulus, 
        exponent
    )

    key_info_for_hash = key_info.replace('<ds:KeyInfo', '<ds:KeyInfo ' + XML_NAMESPACES)

    sha1_certificate = sha1_base64(key_info_for_hash.encode('UTF-8'))

    signed_info = get_signed_info(
        signed_info_number, 
        signed_properties_id_number, 
        sha1_signed_properties,
        certificate_number, 
        sha1_certificate, 
        reference_id_number, 
        sha1_invoice,
        signature_number, signed_properties_number
    )

    signed_info_for_signature = signed_info.replace('<ds:SignedInfo', '<ds:SignedInfo ' + XML_NAMESPACES)

    signed_info_for_signature = canonicalize_lxml(signed_info_for_signature)

    signature = keys.key.sign(signed_info_for_signature.encode("utf-8"), padding.PKCS1v15(), SHA1())

    signature = encode_base64(signature)

    signature = split_string_every_n(signature, MAX_LINE_SIZE)

    xades_bes = get_xades_bes(
        xmls=XML_NAMESPACES, 
        signature_number=signature_number, 
        object_number=signature_value_number, 
        signed_info=signed_info, 
        signature=signature, 
        key_info=key_info, 
        signed_properties=signed_properties
    )

    tail_tag = get_xml_end_node(xml_tree)

    #print(type(tail_tag))
    #print(type(xades_bes))
    #print(type(xml))
    
    signed_xml = xml.replace(tail_tag, xades_bes + tail_tag)
    
    return signed_xml


import frappe
from frappe import _
from cryptography.hazmat.backends import default_backend
from frappe.utils.password import get_decrypted_password

class XadesToolV4():
    def sign_xml(self, xml_string_data, doc, signature_doc):
        
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

        if(signature_doc):            
            full_path_p12 = frappe.get_site_path() + signature_doc.p12
            #print(full_path_p12)
            
            with open(full_path_p12, 'rb') as f:
                p12 = f.read()

        signed_xml = sign_xml(p12, password_p12, xml_string_data)
        return signed_xml
