from modelo import *  # Importa las clases generadas
from lxml import etree

# Crear una instancia del modelo
persona = Persona(nombre="John Doe", edad=25)

# Serializar a XML
xml_string = persona.toxml("utf-8")

print(xml_string)


def validar_xml(xml_string, xsd_path):
    xmlschema_doc = etree.parse(xsd_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)

    xml_doc = etree.fromstring(xml_string)

    if xmlschema.validate(xml_doc):
        print("Documento XML válido.")
    else:
        print("Documento XML no válido. Errores:")
        for error in xmlschema.error_log:
            print(error)

xsd_path = "tu_esquema.xsd"
validar_xml(xml_string, xsd_path)