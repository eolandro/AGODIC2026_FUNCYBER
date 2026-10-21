"""
Este programa permite iniciar sesión usando:
* Usuario: el Nombre registrado en la bd
* Contraseña: la contraseña registrada en la bd
* Código: el código temporal que se genera en la app de autenticación
"""

import argparse
import sqlite3
import bcrypt
import pyotp
from pathlib import Path
from getpass import getpass

parser = argparse.ArgumentParser(
	prog = 'iniciarSesion',
	description = 'Inicio de sesión con contraseña y código totp',
	epilog = 'Fundamentos de Cyber'
)

parser.add_argument('BaseDeDatos', type = Path)

def iniciarSesion(rutaDB):
	Nombre = input("Usuario: ")
	PWD = getpass("Contraseña: ")
	Codigo = getpass("Código de autenticación: ").strip()
	con = sqlite3.connect(str(rutaDB.resolve()))
	cur = con.cursor()
	cur.execute("select Hash, Semilla from usuarios where Nombre = ?", [Nombre])
	fila = cur.fetchone()
	con.close()
	if fila is None:
		print("Usuario, contraseña o código incorrecto")
		return False
	HASH, Semilla = fila
	if not bcrypt.checkpw(PWD.encode('utf-8'), HASH.encode('utf-8')):
		print("Usuario, contraseña o código incorrecto")
		return False
	totp = pyotp.TOTP(Semilla)
	if totp.verify(Codigo):
		print(f"¡Bienvenido, {Nombre}!")
		return True
	else:
		print("Usuario, contraseña o código incorrecto.")
		return False

if __name__ == "__main__":
	Argumentos = parser.parse_args()
	if Argumentos.BaseDeDatos.exists():
		intentos = 3
		while intentos > 0:
			if iniciarSesion(Argumentos.BaseDeDatos):
				break
			intentos -= 1
			if intentos > 0:
				print(f"Te quedan {intentos} intento(s).\n")
			else:
				print("Demasiados intentos fallidos.")
	else:
		print("No se encontró la base de datos")
