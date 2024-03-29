from lxml import etree
from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import datetime
#from odoo.addons.ec_sri_authorizathions.models import modules_mapping
import base64

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

class xml_builder:
    def generate_xml_file(self, xml_id, document_id, invoice_type, type_grouped='individual'):
        """Genera estructura xml del archivo a ser firmado
        :param xml_id: identificador xml_data
        :param document_id: identificador del documento a firmar
        :param invoice_type: Puede ser los tipos :
            out_invoice : Factura
            out_refund : Nota de Credito
            debit_note_out : Nota de Debito
            delivery_note : Guia de Remision
            withhold_purchase : Comprobante de Retencion
            lote_masivo : Lote Masivo
        :param type_grouped: El tipo de agrupado puede ser:
            individual : Individual
            grouped : Lotes Masivos
        :rtype: objeto root agregado con info tributaria
        """

        util_model = self.env['ecua.utils']
        key_model = self.env['sri.keys']
        company = self.printer_id.shop_id.company_id
        sign_now = self.env.context.get('sign_now',True)
        xml_data = self.browse(xml_id)
        document_type = modules_mapping.get_document_type(invoice_type)
        field_name = modules_mapping.get_field_name(document_type)
        model_name = modules_mapping.get_model_name(document_type)
        doc_model = self.env[model_name]
        if not company.documents_electronic_settings_id:
            raise UserError(_("No ha cargado la Firma Electrónica para la compañía %s") % (company.name))
        environment = company.documents_electronic_settings_id.type_environment

        emission = "1"
        document = doc_model.browse(document_id)
        partner_id = document.partner_id
        printer_id = document.printer_id.id
        sequence = ''
        if xml_data.xml_type == 'individual':
            if document[field_name]:
                sequence = self.get_sequence(printer_id, document[field_name])
            else:
                number = document.printer_id.get_next_number_electronic(invoice_type, document.id)
                sequence = self.get_sequence(printer_id, number)
        type_document = XML_HEADERS.get(invoice_type)
        root = Element(type_document, id="comprobante", version=DOCUMENT_VERSIONS.get(invoice_type))
        key_id, clave_acceso, root = self.generate_info_tributaria(xml_id, root, DOCUMENT_TYPES.get(invoice_type),
                                                                   environment, emission, company, printer_id, sequence,
                                                                   document[DOCUMENT_FIELDS_DATE.get(invoice_type)])
        if key_id:
            key_model.write([key_id], {'state': 'used'})
        state = xml_data.state
        if xml_data.external_document:
            type_emision = 'normal'
        else:
            if emission == '1':
                type_emision = 'normal'
            else:
                type_emision = 'contingency'
                state = 'contingency'
        xml_data.write({'type_environment': environment,
                        'type_emision': type_emision,
                        'key_id': key_id,
                        'state': state,
                        'xml_key': clave_acceso,
                        'partner_id': partner_id and partner_id.id or False,
                        })

        if xml_data.invoice_out_id:
            xml_data.invoice_out_id.write({'xml_key': clave_acceso,
                                           'xml_data_id': xml_id,
                                           })
        elif xml_data.credit_note_out_id:
            xml_data.credit_note_out_id.write({'xml_key': clave_acceso,
                                               'xml_data_id': xml_id,
                                               })
        elif xml_data.debit_note_out_id:
            xml_data.debit_note_out_id.write({'xml_key': clave_acceso,
                                              'xml_data_id': xml_id,
                                              })
        elif xml_data.withhold_id:
            xml_data.withhold_id.write({'xml_key': clave_acceso,
                                        'xml_data_id': xml_id,
                                        })
        elif xml_data.invoice_in_id:
            xml_data.invoice_in_id.write({'xml_key': clave_acceso,
                                          'xml_data_id': xml_id,
                                          })
        elif xml_data.delivery_note_id:
            xml_data.delivery_note_id.write({'xml_key': clave_acceso,
                                             'xml_data_id': xml_id,
                                             })

        if sign_now:
            if invoice_type == 'out_invoice':
                doc_model.get_info_factura(document, root)
            #nota de credito
            elif invoice_type == 'out_refund':
                doc_model.get_info_credit_note(document, root)
            #nota de debito
            elif invoice_type == 'debit_note_out':
                doc_model.get_info_debit_note(document, root)
            elif invoice_type == 'withhold_purchase':
                doc_model.get_info_withhold(document, root)
            elif invoice_type == 'delivery_note':
                doc_model.get_info_delivery_note(document, root)
            elif invoice_type == 'liquidation':
                doc_model.get_info_liquidation(document, root)

        util_model.indent(root)
        string_data = tostring(root, encoding="UTF-8")
        self.check_xsd(string_data, DOCUMENT_XSD_FILES.get(invoice_type))
        binary_data = base64.b64encode(string_data)

        self._generate_partner_login(xml_id, document_id, invoice_type)
        return binary_data, type_document