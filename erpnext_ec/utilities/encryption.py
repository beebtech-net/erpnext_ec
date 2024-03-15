from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from Crypto.Random import get_random_bytes
from cryptography.fernet import Fernet
from base64 import b64encode
from base64 import b64decode

import frappe
from frappe import _

from frappe.utils.file_manager import get_file, save_uploaded

def encriptar_datos(datos, clave):
    cifrador = Fernet(clave)
    datos_encriptados = cifrador.encrypt(datos)
    return datos_encriptados


def encrypt_string(input_string, key):
    cipher = AES.new(key.encode("utf8"), AES.MODE_CBC)
    plaintext = input_string.encode('utf-8')
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    return b64encode(cipher.iv + ciphertext).decode('utf-8')

def decrypt_string(encrypted_string, key):
    # Decodifica el string encriptado de base64
    encrypted_data = b64decode(encrypted_string)
    
    # Extrae el vector de inicialización (los primeros 16 bytes)
    iv = encrypted_data[:AES.block_size]
    
    # Extrae el texto cifrado (resto de encrypted_data)
    ciphertext = encrypted_data[AES.block_size:]
    
    # Crea un nuevo objeto AES usando la misma clave y modo, pero con el IV extraído
    cipher = AES.new(key.encode("utf8"), AES.MODE_CBC, iv)
    
    # Desencripta el ciphertext y quita el padding
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    # Devuelve el plaintext decodificado a string
    return plaintext.decode('utf-8')

# Generar una clave segura (deberías almacenarla de manera segura)
#key = get_random_bytes(16)

# Datos de entrada (puedes leer estos datos desde un archivo o de otra fuente)
#input_data = "Este es un ejemplo de datos para encriptar."

# Encriptar los datos
#encrypted_data = encrypt_string(input_data, key)
#print("Datos encriptados:", encrypted_data)

def get_signature(tax_id):
    
    tax_id = '091982695800111'

    #print(frappe.utils.get_url())

    signature_object = frappe.get_last_doc('Sri Signature', filters = { 'tax_id': tax_id})
	#signature_object = frappe.get_doc('Sri Signature','EXP-2024-00097')
    if(signature_object):
        #print(signature_object)
        #print(signature_object.name)
        
        if(signature_object.p12):
            #link = frappe.utils.get_url() + signature_object.p12
            #f = requests.get(link)

            f = get_file(signature_object.p12)
            #print(f)
            #print(len(f[1]))
            input_data = f[1]
            return input_data
        

def get_ecrypted_signature(tax_id):
    
    tax_id = '091982695800111'

    #print(frappe.utils.get_url())

    signature_object = frappe.get_last_doc('Sri Signature', filters = { 'tax_id': tax_id})
	#signature_object = frappe.get_doc('Sri Signature','EXP-2024-00097')
    if(signature_object):
        #print(signature_object)
        #print(signature_object.name)
        
        if(signature_object.p12):
            #link = frappe.utils.get_url() + signature_object.p12
            #f = requests.get(link)

            f = get_file(signature_object.p12)
            #print(f)
            #print(len(f[1]))

            input_data = f[1]
            #print(type(input_data))
            #print(input_data)
            #print(len(input_data))

            #print(Fernet.generate_key())

            #key = "ratonratonquequieresgatoladron.." #32 bytes
            #key = "ratonratonquequi" #16 bytes
            key = b'ZcyY8iHwMVXCNlu2jmGmeNlmyV_URisNjHWlshUf4Fk='

            encrypted_data = encriptar_datos(input_data, key)
            #print("p12 encriptado")
            #print(encrypted_data)

            #decrypted_data = decrypt_string(encrypted_data, key)
            #print("p12 encriptado decripted")
            #print(decrypted_data)

            #input_pwd = "ronaldpassword"
            #encrypted_pwd = encrypt_string(input_pwd, key)
            #print("pwd encriptado")
            #print(encrypted_pwd)
            return encrypted_data        
        

