import chunk
from pdb import lasti2lineno
import socket
import sys
import os
from sha256 import *

PORT = 50010
CLIENTS = 1

s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
s.bind( ('', PORT) )
s.listen( 5 )

dialogos = []
direcciones = []
	
fileContent = open(sys.argv[1], "rb").read()
fileContentDec = fileContent.decode()
CLIENTS = int(sys.argv[2])

while True:

	print("\n  Esperando clientes... (" + str(CLIENTS) + ")")

	# esperar a que la cantidad de clientes especificada por parametro se conecten
	for i in range(CLIENTS):
		dialogo, dir_cli = s.accept()
		dialogos.append(dialogo)
		direcciones.append(dir_cli[0])
		print( "  >> Cliente conectado desde {}:{}.".format( dir_cli[0], dir_cli[1] ) )
	
	# enviar señal de inicio a los clientes
	for i in range(CLIENTS):
		dialogos[i].sendall( "START".encode() )

	# enviar el contenido del archivo a los clientes en trozos de 512 bytes
	for i in range(CLIENTS):
		chunkCont = 0
		while True:
			chunk = fileContentDec[chunkCont:chunkCont+512]
			chunkCont += 512
			dialogos[i].sendall( chunk.encode() )
			if not chunk:
				break

		dialogos[i].sendall( "END".encode() )	# enviar señal de fin de transmision del archivo

	print("\n  ===============================")
	print("     || CLIENTES MINANDO... ||     ")
	print("  ===============================\n")

	# recopiar los nonces de los clientes y calcular el mejor hash de entre todos
	bestHash = None
	bestLastLine = None	
	for i in range(CLIENTS):
		buf = dialogos[i].recv( 512 ).decode()
		lastLine = buf + " G06"
		print(" >> [" + direcciones[i] + "]: " + lastLine)
		local_fileContent = fileContent + lastLine.encode()
		new_hash = generate_hash(local_fileContent).hex()

		if (bestHash == None or bestHash > new_hash):
			bestHash = new_hash
			bestLastLine = lastLine

	# cerrar la conexión con los clientes
	for i in range(CLIENTS):
		dialogos[i].close()
	
	# crear el archivo resultado
	if (os.path.exists("SGSSI-22.CB.02.Paralelo-Red.txt")):
		os.remove("SGSSI-22.CB.02.Paralelo-Red.txt")

	fileContent = fileContent + bestLastLine.encode()
	file = open("SGSSI-22.CB.02.Paralelo-Red.txt", "ab")
	file.write(fileContent)
	file.close()

	print("\n  ==========================")
	print("   || MEJOR RESULTADO ||  ")
	print("  ==========================\n")

	ceros = 0
	for i in range(8):
		if (bestHash[i] == "0"):
			ceros += 1
		else:
			break

	print("Mejor hash (" + str(ceros) + "): " + bestHash)
	print("Archivo resultado generado: \"SGSSI-22.CB.02.Paralelo-Red.txt\"")

	break

s.close()