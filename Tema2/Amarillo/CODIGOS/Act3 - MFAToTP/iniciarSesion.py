"""
Este programa permite iniciar sesión validando:

- Número de empleado
- Contraseña (hash bcrypt guardado en la DB)
- Código de 6 dígitos de la app de autenticación (TOTP)

Si todo es correcto, muestra el mensaje de sesión iniciada y registra en la
tabla asistencia quién entró (id del usuario) y la fecha y hora.

Despues podemos correr el SQL para ver ya con el nombre y en orden DESC quienes han entrado.

"""

import argparse
import sqlite3
import bcrypt
import pyotp
from datetime import datetime
from pathlib import Path
from getpass import getpass


#Máximo de intentos en el ciclo para validar el inicio de sesión.
MAX_INTENTOS = 3

# Hash de relleno: se compara contra él cuando el usuario no existe, para que
#tardar lo mismo y no revelar qué números de empleado están registrados.
HASH_FALSO = bcrypt.hashpw(b"relleno", bcrypt.gensalt())



parser = argparse.ArgumentParser(
	prog='iniciarSesion',
	description='Inicio de sesión con contraseña y código multifactor',
	epilog='Fundamentos de Cyber'
)

parser.add_argument('BaseDeDatos', type=Path)

def buscarUsuario(con, NoEmpleado):
	SQL = "select id, Nombre, Hash, Semilla from usuarios where NoEmpleado = ?"
	return con.execute(SQL, [NoEmpleado]).fetchone()

def validarCredenciales(con, NoEmpleado, PWD, codigo=None):
	"""Regresa (id, nombre) del usuario si todo es válido, o None si algo falla.
	codigo=None significa entrar solo con contraseña (sin verificación en dos pasos)"""
	bPWD = PWD.encode('utf-8')
	usuario = buscarUsuario(con, NoEmpleado)

	try:
		if usuario is None:
			bcrypt.checkpw(bPWD, HASH_FALSO)
			return None

		idUsuario, Nombre, HASH, Semilla = usuario
		pwdOK = bcrypt.checkpw(bPWD, HASH.encode())
	except ValueError:
		#ocurre cuando guardemos una contraseña de más de 72 bytes ya que da error
		return None

	codigoOK = True if codigo is None else pyotp.TOTP(Semilla).verify(codigo, valid_window=1)
	return (idUsuario, Nombre) if (pwdOK and codigoOK) else None



def registrarAsistencia(con, idUsuario):
	"""Guarda en la tabla asistencia quién entró y cuándo. Regresa la fecha y hora"""
	FechaHora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	SQL = "insert into asistencia (idusuarios, FechaHora) values (?, ?)"
	con.execute(SQL, [idUsuario, FechaHora])
	con.commit()
	return FechaHora
	



def iniciarSesion(rutaDB):
	con = sqlite3.connect(str(rutaDB.resolve()))
	try:
		for intento in range(1, MAX_INTENTOS + 1):
			print("\nINICIO DE SESIÓN - [SmartWorkers]")
			NoEmpleado = input("\nNúmero de Empleado: ").strip()
			PWD = getpass("Contraseña: ")
			codigo = input("Código de autenticación: ").replace(" ", "")

			usuario = validarCredenciales(con, NoEmpleado, PWD, codigo)
			if usuario is not None:
				idUsuario, Nombre = usuario
				FechaHora = registrarAsistencia(con, idUsuario)
				print(f"\n¡SESIÓN INICIADA! Bienvenid@, {Nombre}.")
				print(f"Asistencia registrada: {FechaHora}")
				return True

			restantes = MAX_INTENTOS - intento
			print("\nNúmero de empleado, contraseña o código incorrectos.")
			if restantes:
				print(f"Intentos restantes: {restantes}\n")

		print("\nDemasiados intentos fallidos. Acceso denegado.")
		return False
	finally:
		con.close()

if __name__ == "__main__":
	argumentos = parser.parse_args()
	if argumentos.BaseDeDatos.exists():
		iniciarSesion(argumentos.BaseDeDatos)
	else:
		print("\nNo se encontró la DB.")
