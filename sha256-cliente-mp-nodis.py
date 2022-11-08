import socket
import ctypes
import multiprocessing
import time
import random
import os
import signal
import sys
import subprocess
from sha256 import *

# funcion que es ejecutada paralelamente por cada hilo
def calcular(arrNonce):

	maxCeros = 0
	bestHash = "{:08x}".format(4294967295)
	hexaCont = random.randint(0, 4294967295)	# nonce en formato decimal
	identificador = " G06"						# identificador del usuario / alumno
	startTime = time.time()

	fileContentOG = None
	with open("temp.txt", "rb") as escribir:
		fileContentOG = escribir.read()

	# obtener el identificador del hilo hardware
	nombre = (multiprocessing.current_process().name[len(multiprocessing.current_process().name)-1])
	id = int(nombre) - 1

	# bucle principal; conseguir el resumen hash con mayor numero de ceros
	while(time.time() - startTime < 60):

		lastLine = "{:08x}".format(hexaCont) + identificador	# ensamblaje de la ultima linea (nonce hexadecimal + identificador)
		fileContent = fileContentOG + lastLine.encode()			# ensamblaje del contenido del archivo

		new_hash = generate_hash(fileContent).hex()				# obtener el resumen hash usando la libreria sha256.py (https://github.com/keanemind/python-sha-256)

		# comparar si el hash actual es mejor que el mejor historico
		if (bestHash > new_hash):					
			arrNonce[id] = hexaCont
			localCeros = 0
			for i in range(8):
				if (new_hash[i] == "0"):
					localCeros += 1
				else:
					break

			bestHash = new_hash
			maxCeros = localCeros
			print("[" + str(id) + "] Mejor hash actual: (" + str(maxCeros) + ") " + bestHash + " | Nonce: " + str(hexaCont))
        
		hexaCont = random.randint(0, 4294967295)


if __name__ == '__main__':
	fileContent = None

	PORT = 50010

	if len( sys.argv ) != 2:
		print( "Uso: {} <servidor>".format( sys.argv[0] ) )
		exit( 1 )

	# establecer conexion con el servidor
	print("\n  >> Esperando al servidor...")
	dir_serv = (sys.argv[1], PORT)
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	s.connect( dir_serv )

	# esperar señal de inicio del servidor
	print("\n  >> Esperando señal del servidor...")
	buf = s.recv( len("START".encode()) ).decode()

	# recibir el contenido del archivo a usar para el calculo del hash en trozos de 512 bytes
	print("\n  >> Recibiendo datos del archivo...")
	fileContentOG = ""
	while True:
		chunk = s.recv( 512 ).decode()

		chunkLen = len(chunk)
		if chunk[chunkLen-3:chunkLen] == "END":
			chunk = chunk[:-3]
			fileContentOG += chunk
			break

		fileContentOG += chunk
	
	fileContentOG = fileContentOG.encode()
	fileContent = fileContentOG.decode()

	# crear archivo temporal con el contenido del archivo recibido (para ser usado por cada hilo)
	if (os.path.exists("temp.txt")):
		os.remove("temp.txt")

	with open("temp.txt", "wb") as escribir:
		escribir.write(fileContentOG)
		
	time.sleep(1)

	print("\n =============================")
	print("    || CALCULO COMENZADO || ")
	print(" =============================\n")

	# array definido en espacio de memoria compartida para almacenar el nonce de cada hilo
	best_nonce_global = multiprocessing.Array(ctypes.c_int64, multiprocessing.cpu_count())

	# lanzar los trabajos para cada hilo hardware
	arrRef = []
	for i in range(multiprocessing.cpu_count()):
		arrRef.append(multiprocessing.Process(target=calcular, args=(best_nonce_global,)))
		arrRef[i].start()

	# el proceso principal espera a que vuelvan los hilos
	for i in range(multiprocessing.cpu_count()):
		arrRef[i].join()
    
	# esperar a que todos los procesos lleguen a este punto para evitar desincronizacion
	multiprocessing.Barrier(multiprocessing.cpu_count())

	lastLine = None
	bestHash = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF".lower()
	bestLastLine = None

	# obtener el mejor nonce de entre todos los hilos
	print("")
	for i in range(multiprocessing.cpu_count()):
		nonceFinal = "{:08x}".format(best_nonce_global[i]).lower()
		lastLine = nonceFinal + " G06"
		local_fileContent = fileContentOG + lastLine.encode()
        
		final_hash = generate_hash(local_fileContent).hex()

		print("  [" + str(i) + "] >> " + lastLine)
		if (bestHash > final_hash):
			bestHash = final_hash
			bestLastLine = lastLine

	print("\n ==============================")
	print("    || RESULTADOS LOCALES ||   ")
	print(" ==============================\n")
	print("  >> Mejor hash: " + bestHash)
	print("  >> lastLine: " + bestLastLine)

	nonce = bestLastLine[0:8]
	s.sendall( nonce.encode() )		# enviar el mejor nonce al servidor

	s.close()

	os.remove("temp.txt")