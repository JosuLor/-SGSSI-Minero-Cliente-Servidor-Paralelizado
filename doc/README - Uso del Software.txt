SERVIDOR: 
python sha256-server-mp-nodis <archivo a transmitir> <numero de clientes>

ejemplo de uso:
python sha256-server-mp-nodis.py SGSSI-22.CB.01.txt 1

CLIENTE:
python sha256-cliente-mp-nodis <ip del servidor>

ejemplo de uso:
python sha256-cliente-mp-nodis.py 10.110.236.146

El archivo a transmitir puede ser cualquiera. 
El servidor se lo envía a los clientes, y los clientes operan con él.
Al terminar el tiempo establecido (60 segundos), los clientes calculan su mejor hash local y después envían el nonce al servidor.
El servidor recoge todos los mejores nonces de los clientes, y calcula cual es el que mejor resultado da.
Finalmente, el servidor crea el fichero resultado "SGSSI-22.CB-02-Paralelo-Red.txt" localmente.

Ejecutar primero el servidor, y después los clientes.
Solo es necesario que el servidor tenga el archivo a transmitir.
El programa ha sido desarrollado en Windows, y ha sido probado para Windows.
Sin embargo, se ha desarrollado pensando en la compatibilidad con Linux, y gracias a eso, también se puede ejecutar en Linux; ha sido probado en Linux también.

Windows: para conocer la IP a especificar en el cliente, usar el comando ipconfig y ver el apartado "Dirección IPv4" (usar el comando en el PC que hará de servidor)
Linux: lo mismo, pero con el comando ifconfig. Ver el apartado en "eth0".