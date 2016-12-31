#!/usr/bin/env python

import mraa
import time
import MySQLdb
import sys


TRIG_PIN = 12 #Puerto en el que hay el Trigger
ECHO_PIN=[13,11] #Puertos en los que hay nuestros pins de Echo
idIntel=0 #Id de nuestra Intel
echo=[] #Array en la que almacenaremos nuestros pins una vez los definamos y activemos
ocupacions=[]
trig=mraa.Gpio(12) #Inicialitzamos el pin de Trigger
trig.dir(mraa.DIR_OUT) #Lo definimos como pin de salida
for i in range(len(ECHO_PIN)): #Para todos los pins de Echo que tengmos
	echo.append(mraa.Gpio(ECHO_PIN[i])) #Inicializamos los pins de Echo y los guardamos en l'array Echo
	echo[i].dir(mraa.DIR_IN) #Los definimos como pins de entrada


#Funcio que llegeix el sensor i retorna la distancia en cm
def readURM(pos):
	start=0 #Inicializamos las variables del timer 
	stop=0
	#Enviamos el pulso del Trigger de 10 us
	trig.write(0)
	time.sleep(2/1000000)
	trig.write(1)
	time.sleep(10/1000000)
	trig.write(0)
	#Calculamos el tiempo que pass hasta que recibimos el pulso de Echo
	while echo[pos].read()==0:
	  start = time.time()

	while echo[pos].read()==1:
	  stop = time.time()

	#Transformamos los microsegundos en centimetros
	cm=(stop-start)*1000000/29/2
	return cm

#Funcio que determina si el valor obtingut del sensor denota presencia o no
def detection(pos):
	UMBRAL=24 #Definimos el umbral
	d=readURM(pos)
	tout=10 #definimos el TimeOut
	t=0
	while (d<0 or d>450) and t<tout: #Si se ha producido un error de lectura volvemos a leer hasta TimeOut
		d=readURM(pos)
		t+=1
 
	if d<UMBRAL: #Si la distancia es menor al umbral senyalamos deteccion y retornamos 1
		print(d)
		return 1
	else:
		print(d) #Si la distancia es mayor al umbral senyalamos no deteccion y retornamos 0
		return 0

def updatedb(o, ids, idi):
	#Definimos la accion que queremos hacer sobre la tabla
	query="""UPDATE biblioteca.biblioteca SET estat=%s WHERE (idSensor=%s AND idIntel=%s)""" 
	data=(o, ids, idi) #Especificamos los datos a anyadir
	#Creamos una conexion con nuestra tabla 
	#donde la IP corresponde a la IP del ordenador donde esta el servidor
	conn=MySQLdb.connect(host="10.0.60.237",user="usr1", passwd="usr1",db="biblioteca")
	cursor=conn.cursor() #Creamos el cursor
	cursor.execute(query, data) #ejecutamos la accion
	conn.commit()
	#Cerramos las comunicaciones
	cursor.close()
	conn.close()


while True:
	for i in range(len(ECHO_PIN)): #Para todos los sensores
		dete=detection(i); #Buscamos su estado actual
		ocupacions.insert(i, dete) #La anyadimos a nuestra array
		updatedb(ocupacions[i], i, idIntel) #Actualizamos la base de
	time.sleep(5)

