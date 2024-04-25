from lxml import etree
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.etree import ElementTree
import xml.etree.ElementTree as ET


from datetime import datetime
#from odoo.addons.ec_sri_authorizathions.models import modules_mapping
import base64

import time
import frappe
from frappe import _
import erpnext
import os

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
            campo_adicional.text = campo_adicional.find("text").text
            
            campo_adicional.remove(campo_adicional.find("nombre"))
            campo_adicional.remove(campo_adicional.find("text"))
    return xml_tree
    

@frappe.whitelist()
def build_xml(doc_name, typeDocSri, typeFile, siteName):

    # Datos para generar el XML
    data = {
        "infoTributaria": {
            "ambiente": "1",
            "tipoEmision": "1",
            "razonSocial": "Razón Social",
            "nombreComercial":"nombreComercial",
            "ruc":"0919826958001",
            "claveAcceso":"2003202401179071031900122160010001408395658032312",
            "codDoc": "01",
            "estab" : "216",
            "ptoEmi" : "001",
            "secuencial" : "000140839",
            "dirMatriz" : "KM CINCO Y MEDIO AV DE LOS SHYRIS N SN Y SECUNDARIA"
        },
        "infoFactura": {
            "fechaEmision": "20/03/2024",
            "dirEstablecimiento": "VIA A LA COSTA KM 9.8 JUNTO A LA",
            "contribuyenteEspecial": "5368",
            "obligadoContabilidad": "SI",
            "tipoIdentificacionComprador": "05",
            "razonSocialComprador": "CHONILLO VILLON RONALD STALIN",
            "identificacionComprador": "0919826958",
            "totalSinImpuestos": "20.69",
            "totalDescuento": "0",
            "totalConImpuestos": {
                "totalImpuesto": {
                    "codigo": "2",
                    "codigoPorcentaje": "0",
                    "baseImponible": "20.69",
                    "tarifa": "0",
                    "valor": "0.00"
                }
            },
            "propina": "0.00",
            "importeTotal": "20.69",
            "moneda": "DOLAR",
            "pagos": {
                "pago": {
                    "formaPago": "19",
                    "total": "20.69",
                    "plazo": "0",
                    "unidadTiempo": "MESES"
                }
            }
        },
        "detalles": {
            "detalle": [
            {
                "codigoPrincipal": "100027114",
                "descripcion": "CONRELAX.CONRELAX PLUS TABS. 504 MG C10 SUELTAS",
                "cantidad": "5",
                "precioUnitario": "2.09",
                "descuento": "0",
                "precioTotalSinImpuesto": "10.45",
                "impuestos": {
                "impuesto": {
                    "codigo": "2",
                    "codigoPorcentaje": "0",
                    "tarifa": "0",
                    "baseImponible": "10.45",
                    "valor": "0.00"
                }
                }
            },
            {
                "codigoPrincipal": "244624",
                "descripcion": "NEOGAIVAL.NEOGAIVAL 2 MG CJA X20 SUELTAS",
                "cantidad": "10",
                "precioUnitario": "0.384",
                "descuento": "0",
                "precioTotalSinImpuesto": "3.84",
                "impuestos": {
                "impuesto": {
                    "codigo": "2",
                    "codigoPorcentaje": "0",
                    "tarifa": "0",
                    "baseImponible": "3.84",
                    "valor": "0.00"
                }
                }
            },
            {
                "codigoPrincipal": "140376",
                "descripcion": "PANALGESIC.PANALGESIC FORTE CREMA 32 GR",
                "cantidad": "2",
                "precioUnitario": "3.2",
                "descuento": "0",
                "precioTotalSinImpuesto": "6.4",
                "impuestos": {
                "impuesto": {
                    "codigo": "2",
                    "codigoPorcentaje": "0",
                    "tarifa": "0",
                    "baseImponible": "6.40",
                    "valor": "0.00"
                }
                }
            }
            ]
        },
        "infoAdicional": {
            "campoAdicional": 
            [
                {
                    "nombre": "DIRECCION",
                    "text": "SP SN SI"
                },
                {
                    "nombre": "DESCUENTO",
                    "text": "1.01"
                }
            ]
        }
    }

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

    print(xml_str.decode())

    return xml_str.decode()
