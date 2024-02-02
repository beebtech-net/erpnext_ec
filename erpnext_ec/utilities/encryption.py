from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from base64 import b64encode

def encrypt_string(input_string, key):
    cipher = AES.new(key.encode("utf8"), AES.MODE_CBC)
    plaintext = input_string.encode('utf-8')
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    return b64encode(cipher.iv + ciphertext).decode('utf-8')

# Generar una clave segura (deberías almacenarla de manera segura)
#key = get_random_bytes(16)

# Datos de entrada (puedes leer estos datos desde un archivo o de otra fuente)
#input_data = "Este es un ejemplo de datos para encriptar."

# Encriptar los datos
#encrypted_data = encrypt_string(input_data, key)
#print("Datos encriptados:", encrypted_data)