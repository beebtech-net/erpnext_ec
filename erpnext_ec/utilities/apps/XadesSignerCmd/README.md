#XadesSignerCmd
Es una herramienta creada con .net Core
Sirve para firmar archivos XML específicamente para el SRI Ecuador

#Requerimientos
.Net Core Runtime 6.0

sudo apt install zlib1g

sudo apt-get update && \
  sudo apt-get install -y aspnetcore-runtime-6.0


Ubuntu:
    Ejecutar con su (root)
    chmod +x XadesSignerCmd

./XadesSignerCmd --fileinput contenido.xml --p12 firma.p12 --password aquipassword --output contenido_signed.xml