"""
Este programa tiene como objetivo:
*Agregar Nombre
*Agregar Contraseña
*Generar Semilla para app auth
"""

import argparse
import sqlite3
from pathlib import Path
from getpass import getpass
import bcrypt
import pyotp


parser = argparse.ArgumentParser(
    prog='registrarUsuario',
    description='Agrega usuarios a una base de datos',
    epilog='Fundamentos de Cyber'
)

parser.add_argument('BaseDeDatos', type=Path) 

def registrarUsuario(rutaDB):
    con = sqlite3.connect(str(rutaDB.resolve()))
    NoEmpleado = input("Ingrese el numero de empleado: ")
    Nombre = input("Ingrese el nombre del usuario: ")
    PWD = getpass("Ingrese la contraseña del usuario: ")
    bPWD = PWD.encode('utf-8')
    salt = bcrypt.gensalt()
    HASH = bcrypt.hashpw(bPWD, salt).decode()
    Semilla = pyotp.random_base32()
    SQL = "INSERT INTO Usuarios values(Null, ?, ?, ?, ?)"
    cursor = con.cursor()

    try:
        cursor.execute(SQL, [NoEmpleado, Nombre, HASH, Semilla])
        con.commit()
    except sqlite3.IntegrityError:
        print(f"\n[!] Error: El número de empleado '{NoEmpleado}' ya está registrado.")
        con.close()
        return

    print(f"\nSemilla: {Semilla}")
    uri = pyotp.totp.TOTP(Semilla).provisioning_uri(
        name=f"{Nombre}@empresa.com", issuer_name="asistencia app"
    )
    print(f"URI de aprovisionamiento: {uri}")
    
    con.close()
    print("adios !!!")


if __name__ == "__main__":
    Argumentos = parser.parse_args()
    if Argumentos.BaseDeDatos.exists():
        print("Se encontro la base de datos")
        registrarUsuario(Argumentos.BaseDeDatos)
    else:
        print("No se encontro la base de datos")