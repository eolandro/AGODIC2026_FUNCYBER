"""

Este programa tiene como objetivo agregar
nuevos usuarios a la base de datos.

Permitiendo lo siguiente:
* Agregar Nombre
* Agregar Contraseña
* Generar Semilla para app de auth

"""
import argparse
import sqlite3
import bcrypt
import pyotp
import qrcode
from pathlib import Path
from getpass import getpass

parser = argparse.ArgumentParser(
	prog = 'registrarUsuario',
	description = 'Agrega usuarios a una base de datos',
	epilog = 'Fundamentos de Cyber'
)
parser.add_argument('BaseDeDatos', type = Path)

def registrarUsuario(rutaDB):
	con = sqlite3.connect(str(rutaDB.resolve()))
	NoEmpleado = input("Numero de Empleado: ")
	Nombre = input("Nombre: ")
	PWD = getpass("Contraseña: ")
	bPWD = PWD.encode('utf-8')
	salt = bcrypt.gensalt()
	HASH = bcrypt.hashpw(bPWD, salt).decode()
	Semilla = pyotp.random_base32()
	SQL = "insert into usuarios values(NULL,?,?,?,?)"
	cur = con.cursor()
	cur.execute(SQL,[NoEmpleado,Nombre,HASH,Semilla])
	con.commit()
	URI = pyotp.totp.TOTP(Semilla).provisioning_uri(
		name=Nombre, issuer_name='Asistencia App'
	)
	con.close()
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=1,
		border=2
	)
	qr.add_data(URI)
	qr.make(fit=True)
	qr.print_ascii(invert=True)
	print("Adios!")

if __name__ == "__main__":
	Argumentos = parser.parse_args()
	if Argumentos.BaseDeDatos.exists():
		print("Se encontro la base de datos.")
		registrarUsuario(Argumentos.BaseDeDatos)
	else:
		print("No se encontro la base de datos")
