"""
Este programa tiene como objetivo agregar  nuevos usuarios a la base de datos.

Permitiendo lo siguiente:
* Agregar Nombre
*Agregar Contraseña
* Generar semilla para app de auth
"""

"""
Este programa tiene como objetivo agregar  nuevos usuarios a la base de datos.

Permitiendo lo siguiente:
* Agregar Nombre
*Agregar Contraseña
* Generar semilla para app de auth
"""

import argparse
from pathlib import Path
import sqlite3
from getpass import getpass
import bcrypt
import pyotp
import qrcode

parser = argparse.ArgumentParser(
        prog='registrarUsuario',
        description='Agrega usuarios a una base de datos',
        epilog='Fundamentos de cyber')
parser.add_argument('BaseDeDatos', type=Path)

def registrarUsuario(rutaDB):
    con = sqlite3.connect(str(rutaDB.resolve())) 
    NoEmpleado = input("Ingrese el numero de empleado: ")
    Nombre = input("Ingrese el nombre del usuario: ")
    PWQ = getpass("Ingrese la contraseña del usuario: ") 
    bPWQ = PWQ.encode('utf-8')
    salt = bcrypt.gensalt()
    HASH = bcrypt.hashpw(bPWQ, salt).decode()
    semilla = pyotp.random_base32()
    SQL = "insert into usuarios values (NULL,?, ?, ?, ?)"
    cur = con.cursor()
    cur.execute(SQL,[NoEmpleado, Nombre, HASH, semilla])
    con.commit()
    print(semilla)
    uri = pyotp.totp.TOTP(semilla).provisioning_uri(name=Nombre, issuer_name="Asistencia App")
    print(uri)
    mostrar_qr(uri)        
    con.close()
    print("Adios")


def login(rutaDB):
    con = sqlite3.connect(str(rutaDB.resolve()))
    cur = con.cursor()
    codigo = input("Ingrese el codigo ToTp: ")
    NoEmpleado = input("Ingrese el numero de empleado: ")
    PWQ = getpass("Ingrese la contraseña del usuario: ")
    cur.execute("select Nombre, hash, semilla from usuarios where NoEmpleado = ?", [NoEmpleado])
    fila = cur.fetchone()
    if pyotp.totp.TOTP(fila[2]).verify(codigo, valid_window=1):
            print(f"Bienvenido {fila[0]}, acceso concedido")
    else:
            print("Codigo ToTp invalido")
    if not fila or not bcrypt.checkpw(PWQ.encode('utf-8'), fila[1].encode('utf-8')):
        print("Credenciales invalidas")
        con.close()
        return


def mostrar_qr(uri):
    qr = qrcode.QRCode(border=1)
    qr.add_data(uri)
    qr.make(fit=True)
    qr.print_ascii(invert=True)


def menu(rutaDB):
    while True:
        print("\n1) Alta de usuario")
        print("2) Acceso a la aplicacion")
        print("3) Salir")
        op = input("Opcion: ")
        if op == "1":
            registrarUsuario(rutaDB)
        elif op == "2":
            login(rutaDB)
        elif op == "3":
            print("Adios")
            break


if __name__ == '__main__':
    Argumentos = parser.parse_args()
    if Argumentos.BaseDeDatos.exists():
        print("Se encontro la base de datos")
        menu(Argumentos.BaseDeDatos)     
    else:
        print("No se encontro la base de datos")


#Aeyis

#vamos a usar totp

#Aeyis

#vamos a usar totp