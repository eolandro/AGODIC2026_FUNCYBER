"""
ESTE PROGRAMA TIENE OBJETIVO AGREGAR NUEVOS USUARIOS A LA BASE DE DATOS

PERMITIEDNO LO SIGUIENTE
* AGREGAR NOMBRE
* AGREGAR CONTRASENA
* GENERAR SEMILLA PARA APP DE AUTH

"""

#Ambiente Virtual del Proyecto: & "C:\Users\hallo\AppData\Local\pypoetry\Cache\virtualenvs\ast-GPrIULS1-py3.14\Scripts\activate.ps1"

import argparse
import sqlite3
import bcrypt
import pyotp
import qrcode
from pathlib import Path
from getpass import getpass


parser = argparse.ArgumentParser(
                    prog='registrarUsuario',
                    description='Agrega usuarios a una base de datos',
                    epilog='Fundamentos de Cyber')

parser.add_argument('BaseDeDatos', type=Path) 

def registrarUsuario(rutaDB):
    con = sqlite3.connect(str(rutaDB.resolve()))
    NoEmpleado = input("Numero de empleado: ")
    Nombre = input("Nombre del usuario: ")
    PWD = getpass("Contraseña: ")
    bPWD = PWD.encode('utf-8')
    salt = bcrypt.gensalt()
    HASH = bcrypt.hashpw(bPWD, salt).decode()
    Semilla = pyotp.random_base32()
    SQL = "INSERT INTO Usuarios VALUES (NULL, ?, ?, ?, ?)"
    cursor = con.cursor()
    cursor.execute(SQL, [NoEmpleado, Nombre, HASH, Semilla])
    con.commit()
    URI = pyotp.totp.TOTP(Semilla).provisioning_uri(
        name=f"{Nombre}@correo.com", issuer_name="Asistencia App"
    )
    qr = qrcode.QRCode()
    qr.add_data(URI)
    qr.make(fit=True)
    qr.print_ascii(invert=True)
    nombreImagen = f"qrcode_{NoEmpleado}.png"
    img = qrcode.make(URI)
    img.save(nombreImagen)
    con.close()
    print("Adios")


if __name__ == "__main__":
    Argumentos = parser.parse_args()
    if Argumentos.BaseDeDatos.exists():
        print("Se encontro la base de datos")
        registrarUsuario(Argumentos.BaseDeDatos)
    else:
        print("No se encontro la base de datos")