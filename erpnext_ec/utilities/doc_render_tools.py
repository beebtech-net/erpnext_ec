import barcode
from barcode.writer import ImageWriter
from barcode.writer import SVGWriter

import base64
from io import BytesIO

def get_barcode_base64(string_code):

    # Generar código de barras Code 39
    code39 = barcode.get_barcode_class('code39')
    barcode_instance = code39(string_code, writer=ImageWriter(), add_checksum=False)

    # Guardar como imagen en memoria
    buffer = BytesIO()
    barcode_instance.write(buffer)
    buffer.seek(0)

    # Convertir la imagen a base64
    base64_image = base64.b64encode(buffer.read()).decode('utf-8')

    # Imprimir la cadena base64
    print(base64_image)
    return base64_image


def get_barcode_svg(string_code):
    # Generar código de barras Code 39
    code39 = barcode.get_barcode_class('code39')
    barcode_instance = code39(string_code, writer=SVGWriter(), add_checksum=False)

    # Obtener el código SVG como texto
    svg_code = barcode_instance.render()

    # Imprimir el código SVG
    print(svg_code)
    return svg_code

