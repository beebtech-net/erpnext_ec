# -*- coding: utf-8 -*-
import base64
import uuid
from datetime import datetime

from lxml import etree
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


NS_DS = "http://www.w3.org/2000/09/xmldsig#"
NS_XADES = "http://uri.etsi.org/01903/v1.3.2#"

NSMAP = {
    "ds": NS_DS,
    "xades": NS_XADES
}


def _c14n(element):
    return etree.tostring(
        element,
        method="c14n",
        exclusive=False,
        with_comments=False
    )


def _sha1(data):
    digest = hashes.Hash(hashes.SHA1(), backend=default_backend())
    digest.update(data)
    return base64.b64encode(digest.finalize()).decode()


def sign_xml(xml_string, p12_bytes, password):
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml_string.encode(), parser)

    private_key, cert, _ = pkcs12.load_key_and_certificates(
        p12_bytes,
        password.encode(),
        backend=default_backend()
    )

    cert_der = cert.public_bytes(encoding=etree.serialization.Encoding.DER)
    cert_b64 = base64.b64encode(cert_der).decode()

    signature_id = "Signature-" + str(uuid.uuid4())
    signed_props_id = "SignedProperties-" + str(uuid.uuid4())
    reference_id = "Reference-" + str(uuid.uuid4())

    # =========================
    # Signature node
    # =========================
    signature = etree.SubElement(root, etree.QName(NS_DS, "Signature"), nsmap=NSMAP)
    signature.set("Id", signature_id)

    signed_info = etree.SubElement(signature, etree.QName(NS_DS, "SignedInfo"))

    canon_method = etree.SubElement(signed_info, etree.QName(NS_DS, "CanonicalizationMethod"))
    canon_method.set("Algorithm", "http://www.w3.org/TR/2001/REC-xml-c14n-20010315")

    sig_method = etree.SubElement(signed_info, etree.QName(NS_DS, "SignatureMethod"))
    sig_method.set("Algorithm", "http://www.w3.org/2000/09/xmldsig#rsa-sha1")

    # =========================
    # Reference to XML
    # =========================
    ref = etree.SubElement(signed_info, etree.QName(NS_DS, "Reference"))
    ref.set("URI", "")

    transforms = etree.SubElement(ref, etree.QName(NS_DS, "Transforms"))

    t1 = etree.SubElement(transforms, etree.QName(NS_DS, "Transform"))
    t1.set("Algorithm", "http://www.w3.org/2000/09/xmldsig#enveloped-signature")

    t2 = etree.SubElement(transforms, etree.QName(NS_DS, "Transform"))
    t2.set("Algorithm", "http://www.w3.org/TR/2001/REC-xml-c14n-20010315")

    digest_method = etree.SubElement(ref, etree.QName(NS_DS, "DigestMethod"))
    digest_method.set("Algorithm", "http://www.w3.org/2000/09/xmldsig#sha1")

    digest_value = etree.SubElement(ref, etree.QName(NS_DS, "DigestValue"))

    # =========================
    # XAdES Object
    # =========================
    obj = etree.SubElement(signature, etree.QName(NS_DS, "Object"))

    qualifying = etree.SubElement(obj, etree.QName(NS_XADES, "QualifyingProperties"))
    qualifying.set("Target", "#" + signature_id)

    signed_props = etree.SubElement(qualifying, etree.QName(NS_XADES, "SignedProperties"))
    signed_props.set("Id", signed_props_id)

    signed_sig_props = etree.SubElement(signed_props, etree.QName(NS_XADES, "SignedSignatureProperties"))

    signing_time = etree.SubElement(signed_sig_props, etree.QName(NS_XADES, "SigningTime"))
    signing_time.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    signing_cert = etree.SubElement(signed_sig_props, etree.QName(NS_XADES, "SigningCertificate"))
    cert_node = etree.SubElement(signing_cert, etree.QName(NS_XADES, "Cert"))

    cert_digest = etree.SubElement(cert_node, etree.QName(NS_XADES, "CertDigest"))
    cert_digest_method = etree.SubElement(cert_digest, etree.QName(NS_DS, "DigestMethod"))
    cert_digest_method.set("Algorithm", "http://www.w3.org/2000/09/xmldsig#sha1")

    cert_digest_value = etree.SubElement(cert_digest, etree.QName(NS_DS, "DigestValue"))
    cert_digest_value.text = _sha1(cert_der)

    issuer_serial = etree.SubElement(cert_node, etree.QName(NS_XADES, "IssuerSerial"))

    issuer_name = etree.SubElement(issuer_serial, etree.QName(NS_DS, "X509IssuerName"))
    issuer_name.text = cert.issuer.rfc4514_string()

    serial_number = etree.SubElement(issuer_serial, etree.QName(NS_DS, "X509SerialNumber"))
    serial_number.text = str(cert.serial_number)

    # =========================
    # Reference to SignedProperties
    # =========================
    ref2 = etree.SubElement(signed_info, etree.QName(NS_DS, "Reference"))
    ref2.set("Type", "http://uri.etsi.org/01903#SignedProperties")
    ref2.set("URI", "#" + signed_props_id)

    digest_method2 = etree.SubElement(ref2, etree.QName(NS_DS, "DigestMethod"))
    digest_method2.set("Algorithm", "http://www.w3.org/2000/09/xmldsig#sha1")

    digest_value2 = etree.SubElement(ref2, etree.QName(NS_DS, "DigestValue"))

    # =========================
    # Digest cálculo
    # =========================
    digest_value.text = _sha1(_c14n(root))
    digest_value2.text = _sha1(_c14n(signed_props))

    # =========================
    # SignatureValue
    # =========================
    signed_info_c14n = _c14n(signed_info)

    signature_value = private_key.sign(
        signed_info_c14n,
        padding=__import__("cryptography.hazmat.primitives.asymmetric.padding").hazmat.primitives.asymmetric.padding.PKCS1v15(),
        algorithm=hashes.SHA1()
    )

    sig_value_node = etree.SubElement(signature, etree.QName(NS_DS, "SignatureValue"))
    sig_value_node.text = base64.b64encode(signature_value).decode()

    # =========================
    # KeyInfo
    # =========================
    key_info = etree.SubElement(signature, etree.QName(NS_DS, "KeyInfo"))
    x509_data = etree.SubElement(key_info, etree.QName(NS_DS, "X509Data"))

    x509_cert = etree.SubElement(x509_data, etree.QName(NS_DS, "X509Certificate"))
    x509_cert.text = cert_b64

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8")


##################################################

file_doc = frappe.get_doc("File", file_id)
p12_bytes = file_doc.get_content()

##################################################
from erpnext_ec.sri.signer import sign_xml

signed_xml = sign_xml(
    xml_string=xml_generado,
    p12_bytes=p12_bytes,
    password=clave_certificado
)

##################################################

def before_submit(doc, method):
    xml = generar_xml_sri(doc)
    firmado = sign_xml(xml, p12_bytes, password)
    doc.xml_firmado = firmado
