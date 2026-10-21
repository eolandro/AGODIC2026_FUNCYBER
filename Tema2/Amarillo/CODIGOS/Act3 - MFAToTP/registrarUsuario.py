"""
Equipo: AMARILLO

Este programa tiene como objetivo agregar nuevos
usuarios a la base de datos, permitiendo lo siguiente:

- Agregar nombre
- Agregar contraseña
- Generar semilla para app de autenticación
- Mostrar el código QR para escanearlo con la app de autenticación

"""

import argparse
import sqlite3
import bcrypt
import pyotp
import segno
from pathlib import Path
from getpass import getpass

#esto es lo que aparece en g Auth
EMISOR = 'ASISTENCIA APP [SmartWorkers]'

parser = argparse.ArgumentParser(
	prog='registrarUsuario',
	description='Agrega usuarios a una DB',
	epilog='Fundamentos de Cyber'
)

parser.add_argument('BaseDeDatos', type=Path)
parser.add_argument(
	'--png',
	action='store_true',
	help='Guarda además el QR como imagen PNG en la carpeta actual'
)

def mostrarQR(URI, NoEmpleado, guardarPNG):
	qr = segno.make(URI, error='m')

	print("\nEscanea este código con tu app de autenticación:\n")
	qr.terminal(compact=True)

	if guardarPNG:
		ruta = Path(f"qr_{NoEmpleado}.png")
		qr.save(str(ruta), scale=8, border=4)
		print(f"\nQR guardado en: {ruta.resolve()}")
		print("(Bórralo después de escanearlo: contiene la semilla.)")

def registrarUsuario(rutaDB, guardarPNG=False):
	print("\n\nREGISTRAR USUARIO - [SmartWorkers]")
	NoEmpleado = input("\nNúmero de Empleado: ").strip()
	Nombre = input("Nombre de Empleado: ").strip()

	if not NoEmpleado or not Nombre:
		print("\nEl número y el nombre de empleado son obligatorios.")
		return

	PWD = getpass("Contraseña: ")
	if PWD != getpass("Confirma la contraseña: "):
		print("\nLas contraseñas no coinciden.")
		return

	bPWD = PWD.encode('utf-8')
	if not bPWD or len(bPWD) > 72:
		# bcrypt solo admite hasta 72 bytes
		print("\nLa contraseña no puede estar vacía ni pasar de 72 bytes.")
		return

	salt = bcrypt.gensalt()
	HASH = bcrypt.hashpw(bPWD, salt).decode()

	Semilla = pyotp.random_base32()

	SQL = "insert into usuarios (NoEmpleado, Nombre, Hash, Semilla) values (?, ?, ?, ?)"
	con = sqlite3.connect(str(rutaDB.resolve()))
	try:
		con.execute(SQL, [NoEmpleado, Nombre, HASH, Semilla])
		con.commit()
	except sqlite3.IntegrityError:
		print(f"\nYa existe un usuario con el número de empleado {NoEmpleado}.")
		return
	finally:
		con.close()

	URI = pyotp.totp.TOTP(Semilla).provisioning_uri(name=NoEmpleado, issuer_name=EMISOR)

	print("\n[ USUARIO REGISTRADO CON ÉXITO! ]")
	mostrarQR(URI, NoEmpleado, guardarPNG)
	print(f"\nCLAVE POR SI NO PUEDE ESCANEAR EL QR: {Semilla}")
	print("\n\n[ HASTA LA PROXIMA! ]")

if __name__ == "__main__":
	argumentos = parser.parse_args()
	if argumentos.BaseDeDatos.exists():
		print("\nSe encontró la DB.")
		registrarUsuario(argumentos.BaseDeDatos, argumentos.png)
	else:
		print("\nNo se encontró la DB.")
		
		
	
	


