import xml.dom.minidom
from lxml import etree
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.etree import ElementTree
import xml.etree.ElementTree as ET
from erpnext_ec.utilities.signature_tool import *
import re

from datetime import datetime
#from odoo.addons.ec_sri_authorizathions.models import modules_mapping
import base64

import time
import frappe
from frappe import _
import erpnext
import os

from erpnext_ec.utilities.doc_builder_fac import *
from erpnext_ec.utilities.doc_builder_grs import build_doc_grs
from erpnext_ec.utilities.doc_builder_cre import build_doc_cre


DOCUMENT_VERSIONS = {
    'out_invoice': '1.1.0',
    'liquidation': '1.1.0',
    'out_refund': '1.1.0',
    'debit_note_out': '1.0.0',
    'delivery_note': '1.1.0',
    'withhold_purchase': '1.0.0',
    'lote_masivo': '1.1.0',
}

DOCUMENT_TYPES = {
    'out_invoice': '01',
    'out_refund': '04',
    'debit_note_out': '05',
    'delivery_note': '06',
    'withhold_purchase': '07',
    'liquidation': '03',
}

DOCUMENT_XSD_FILES = {
    'out_invoice': 'Factura_V1.0.0.xsd',
    'out_refund': 'notaCredito_1.1.0.xsd',
    'debit_note_out': 'notaDebito_1.1.1.xsd',
    'delivery_note': 'guiaRemision_1.1.0.xsd',
    'withhold_purchase': 'comprobanteRetencion_1.1.1.xsd',
    'lote_masivo': 'loteMasivo_1.0.0.xsd',
}

XML_HEADERS = {
    'out_invoice': 'factura',
    'liquidation': 'liquidacionCompra',
    'out_refund': 'notaCredito',
    'debit_note_out': 'notaDebito',
    'delivery_note': 'guiaRemision',
    'withhold_purchase': 'comprobanteRetencion',
    'lote_masivo': 'lote-masivo',
}

DOCUMENT_FIELDS_DATE = {
    'out_invoice': 'invoice_date',
    'out_refund': 'invoice_date',
    'liquidation': 'invoice_date',
    'debit_note_out': 'invoice_date',
    'delivery_note': 'delivery_date',
    'withhold_purchase': 'creation_date',
}

class XMLGenerator:
    def __init__(self, xsd_file):
        self.xsd_file = xsd_file
        self.schema = etree.XMLSchema(file=self.xsd_file)
        self.nsmap = {
            None: "http://www.w3.org/2001/XMLSchema",
            'ds': "http://www.w3.org/2000/09/xmldsig#"
        }

    def generate_xml(self, root_tag, data_dict):
        root = etree.Element(root_tag, nsmap=self.nsmap)
        
        root.set("id","comprobante")
        
        #TODO: Hay que obtener la version desde el XSD
        root.set("version","1.1.0")

        # Crear el árbol XML basado en los datos proporcionados
        self._build_xml(root, data_dict)

        # Crear el documento XML
        xml_doc = etree.ElementTree(root)
        return xml_doc #.getroot()  # Obtener el elemento raíz del árbol XML

    def _build_xml(self, parent, data_dict):
        for key, value in data_dict.items():
            if isinstance(value, dict):
                child = etree.SubElement(parent, key)
                self._build_xml(child, value)
            elif isinstance(value, list):
                for item in value:
                    child = etree.SubElement(parent, key)
                    self._build_xml(child, item)
            else:
                child = etree.SubElement(parent, key)
                child.text = str(value)

    def validate_xml(self, xml_doc):
        try:
            self.schema.assertValid(xml_doc)
            print("El XML es válido según el XSD.")
        except etree.DocumentInvalid as e:
            print("El XML no es válido según el XSD:")
            print(e)

def fix_infoAdicional(xml_tree):
    root = xml_tree.getroot()
    info_adicional = root.find("infoAdicional")
    if info_adicional is not None:
        for campo_adicional in info_adicional.findall("campoAdicional"):
            print(campo_adicional)
            #campo_adicional.set("nombre", campo_adicional.text)
            campo_adicional.set("nombre", campo_adicional.find("nombre").text)
            campo_adicional.text = campo_adicional.find("valor").text
            
            campo_adicional.remove(campo_adicional.find("nombre"))
            campo_adicional.remove(campo_adicional.find("valor"))
    return xml_tree


@frappe.whitelist()
def build_xml_signed(xml_string, data, signature_doc):
    #crear datos para asignar a data
    # 1) desde objeto de datos
    # 2) luego convertirlo a la estructura compatible con el SRI
    #data = {}
    #xml_string = build_xml_data(data, doc_name, typeDocSri, typeFile, siteName)
    signed_xml = SriXmlData.sign_xml(SriXmlData, xml_string, data, signature_doc)
    return signed_xml

@frappe.whitelist()
def get_doc_native(doc, doc_name, typeDocSri, doctype_erpnext, siteName):	
	
	doc_data = None
	
	#doc_object_build = json.loads(doc, object_hook=lambda d: SimpleNamespace(**d))
	
	if typeDocSri == "FAC":			
		doc_data = build_doc_fac(doc_name)	
	elif typeDocSri == "GRS":
		doc_data = build_doc_grs(doc_name)			
	elif typeDocSri == "CRE":
		doc_data = build_doc_cre(doc_name)	

	return doc_data


#Download XML
@frappe.whitelist()
def build_xml(doc_name, typeDocSri, typeFile, siteName):
    #crear datos para asignar a data
    # 1) desde objeto de datos
    # 2) luego convertirlo a la estructura compatible con el SRI
    
    doc = {}
    doctype_erpnext = ''

    data = get_doc_native(doc, doc_name, typeDocSri, doctype_erpnext, siteName)

    xml_beautified = build_xml_data(data, doc_name, typeDocSri, siteName)
    #print(xml_beautified)
    #Inicia la descarga
    frappe.local.response.filename = doc_name + "." + typeFile
    frappe.local.response.filecontent = xml_beautified
    frappe.local.response.type = "download"

@frappe.whitelist()
def build_xml_data(data_object, doc_name, typeDocSri, siteName):

    typeFile = "xml"
    #print('Clave de acceso buscada: "2003202401179071031900122160010001408395658032312"')

    #print(data_object)

    # Datos para generar el XML
    data = build_doc_fac_sri(data_object)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Nombre del archivo XSD
    xsd_file = dir_path + "/xsd/factura_V1/1/0.xsd"
    xmldsig_xsd_path = dir_path + "/xsd/xmldsig-core-schema.xsd"
    
    # Crear instancia del generador XML
    xml_generator = XMLGenerator(xsd_file) #, xmldsig_xsd_path)

    # Generar el XML
    xml_doc = xml_generator.generate_xml("factura", data)

    xml_doc = fix_infoAdicional(xml_doc)

    # Validar el XML con respecto al XSD
    validationResult = xml_generator.validate_xml(xml_doc.getroot())

    if(not validationResult):
        print("No debe retornar nada")
        #return ""
    #frappe.local.response.filename = doc_name + "." + typeFile
    #frappe.local.response.filecontent = response.content
    #frappe.local.response.type = "download"

    xml_str = ElementTree.tostring(xml_doc.getroot(), encoding='utf-8')
    xml_beautified = xml.dom.minidom.parseString(xml_str).toprettyxml()

    #encoding="UTF-8" standalone="no"
    #<factura id="comprobante" version="1.1.0">

    #print(xml_beautified)
    #frappe.local.response.filename = doc_name + "." + typeFile
    #frappe.local.response.filecontent = xml_beautified
    #frappe.local.response.type = "download"

    return xml_beautified
