import argparse
import sqlite3
from pathlib import Path
from getpass import getpass
import bcrypt
import pyotp

parser = argparse.ArgumentParser(
    prog='loginUsuario',
    description='Valida el acceso de usuarios con TOTP y contraseña',
    epilog='Fundamentos de Cyber'
)

parser.add_argument('BaseDeDatos', type=Path)

def iniciarSesion(rutaDB):
    con = sqlite3.connect(str(rutaDB.resolve()))
    cursor = con.cursor()

    NoEmpleado = input("Ingrese el número de empleado: ")

    # Consultamos primero al usuario para obtener sus credenciales
    SQL = "SELECT * FROM Usuarios WHERE NoEmpleado = ?"
    cursor.execute(SQL, [NoEmpleado])
    resultado = cursor.fetchone()
    con.close()

    if not resultado:
        print("\n[!] Error: El número de empleado no está registrado.")
        return

    nombre_usuario = resultado[2]
    hash_guardado = resultado[3]
    semilla_guardada = resultado[4]

    # 1. Solicitar y validar primero el código de 6 dígitos (TOTP)
    codigo_totp = input("Ingrese el código de 6 dígitos : ")
    totp = pyotp.TOTP(semilla_guardada)

    if not totp.verify(codigo_totp):
        print("\n[!] Error: El código de Authenticator es inválido o ha expirado.")
        return

    # 2. Solicitar y validar la contraseña después del TOTP
    PWD = getpass("Ingrese la contraseña del usuario: ")

    if not bcrypt.checkpw(PWD.encode('utf-8'), hash_guardado.encode('utf-8')):
        print("\n[!] Error: Contraseña incorrecta.")
        return

    print(f"\n¡Bienvenido, {nombre_usuario}! Acceso concedido con éxito.")

if __name__ == "__main__":
    Argumentos = parser.parse_args()
    if Argumentos.BaseDeDatos.exists():
        print("Se encontró la base de datos")
        iniciarSesion(Argumentos.BaseDeDatos)
    else:
        print("No se encontró la base de datos")