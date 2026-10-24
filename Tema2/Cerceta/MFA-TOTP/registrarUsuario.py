import sqlite3
import argparse
import bcrypt
import pyotp
import qrcode
from pathlib import Path
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, simpledialog

parser = argparse.ArgumentParser(description="GUI para MFA con SQLite")
parser.add_argument("basededatos", type=Path, nargs="?", default=Path("basededatos.sqlite"))

# ---------------------------------------------------------
# Lógica de Base de Datos y Autenticación
# ---------------------------------------------------------

def registrar_usuario_db(ruta_db, no_empleado, nombre, pwd):
    try:
        con = sqlite3.connect(str(ruta_db.resolve()))
        b_pwd = pwd.encode('utf-8')
        salt = bcrypt.gensalt()
        hash_pw = bcrypt.hashpw(b_pwd, salt).decode()
        semilla = pyotp.random_base32()

        sql = "INSERT INTO usuarios VALUES (NULL, ?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(sql, [no_empleado, nombre, hash_pw, semilla])
        con.commit()

        uri = pyotp.totp.TOTP(semilla).provisioning_uri(name=nombre, issuer_name='Asistencia App')
        
        nombre_archivo_qr = f"qr_{no_empleado}.png"
        img_qr = qrcode.make(uri)
        img_qr.save(nombre_archivo_qr)

        con.close()
        return True, "Registro exitoso.", nombre_archivo_qr
    except sqlite3.IntegrityError:
        return False, f"El número de empleado '{no_empleado}' ya existe.", None
    except Exception as e:
        return False, f"Error al registrar: {str(e)}", None


def verificar_credenciales(ruta_db, no_empleado, pwd):
    con = sqlite3.connect(str(ruta_db.resolve()))
    cur = con.cursor()
    cur.execute("SELECT HASH, Semilla FROM usuarios WHERE NoEmpleado = ?", [no_empleado])
    resultado = cur.fetchone()
    con.close()

    if not resultado:
        return False, "Usuario no encontrado en la base de datos.", None

    hash_guardado, semilla = resultado

    try:
        if bcrypt.checkpw(pwd.encode('utf-8'), hash_guardado.encode('utf-8')):
            return True, "Contraseña correcta.", semilla
        else:
            return False, "Contraseña incorrecta.", None
    except ValueError:
        return False, "El formato de la contraseña guardada en la base de datos no es válido.", None


# ---------------------------------------------------------
# Interfaz Gráfica 
# ---------------------------------------------------------

class MFA:
    def __init__(self, root, ruta_db):
        self.root = root
        self.ruta_db = ruta_db
        self.root.title("Acceso con MFA")
        ancho_ventana = 450
        alto_ventana = 600
        ancho_pantalla = self.root.winfo_screenwidth()
        alto_pantalla = self.root.winfo_screenheight()
        pos_x = (ancho_pantalla // 2) - (ancho_ventana // 2)
        pos_y = (alto_pantalla // 2) - (alto_ventana // 2)
        self.root.geometry(f"{ancho_ventana}x{alto_ventana}+{pos_x}+{pos_y}")

        tk.Label(root, text="Número de Empleado", font=("Arial", 10, "bold")).pack(pady=(20, 2))
        self.entry_no_empleado = tk.Entry(root, font=("Arial", 11), width=25)
        self.entry_no_empleado.pack(pady=2)

        tk.Label(root, text="Nombre del Empleado", font=("Arial", 10, "bold")).pack(pady=(10, 2))
        self.entry_nombre = tk.Entry(root, font=("Arial", 11), width=25)
        self.entry_nombre.pack(pady=2)

        tk.Label(root, text="Contraseña", font=("Arial", 10, "bold")).pack(pady=(10, 2))
        self.entry_pass = tk.Entry(root, show="*", font=("Arial", 11), width=25)
        self.entry_pass.pack(pady=2)

        tk.Button(
            root, text="Registrar Usuario", command=self.ejecutar_registro,
            bg="#E9BEF7", fg="black", font=("Arial", 10, "bold"), width=20, height=1
        ).pack(pady=(20, 8))
        
        tk.Button(
            root, text="Iniciar Sesión (MFA)", command=self.ejecutar_login,
            bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=20, height=1
        ).pack(pady=2)

        self.label_qr = tk.Label(root)
        self.label_qr.pack(pady=(20, 0))

    def ejecutar_registro(self):
        no_emp = self.entry_no_empleado.get().strip()
        nombre = self.entry_nombre.get().strip()
        pwd = self.entry_pass.get()

        if not no_emp or not nombre or not pwd:
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos.")
            return

        exito, mensaje, ruta_qr = registrar_usuario_db(self.ruta_db, no_emp, nombre, pwd)
        messagebox.showinfo("Registro", mensaje)

        if exito and ruta_qr:
            imagen_pil = Image.open(ruta_qr).resize((200, 200))
            self.img_tk = ImageTk.PhotoImage(imagen_pil)
            self.label_qr.config(image=self.img_tk)

    def ejecutar_login(self):
        no_emp = self.entry_no_empleado.get().strip()
        pwd = self.entry_pass.get()

        if not no_emp or not pwd:
            messagebox.showwarning("Campos vacíos", "Ingresa número de empleado y contraseña.")
            return

        exito_pwd, msg_pwd, semilla = verificar_credenciales(self.ruta_db, no_emp, pwd)

        if not exito_pwd:
            messagebox.showerror("Inicio de Sesión", msg_pwd)
            return

        messagebox.showinfo(
            "Primer Factor Completado",
            "Contraseña correcta. Procede a ingresar tu código TOTP de autenticación."
        )

        codigo_totp = simpledialog.askstring(
            "Segundo Factor (MFA)",
            "Ingresa el código de 6 dígitos de tu aplicación de autenticación:"
        )

        if codigo_totp is None:
            return

        codigo_totp = codigo_totp.strip()

        if not codigo_totp.isdigit() or len(codigo_totp) != 6:
            messagebox.showerror(
                "Código Inválido",
                "El código ingresado debe contener exactamente 6 dígitos."
            )
            return

        totp_verifier = pyotp.TOTP(semilla)
        if totp_verifier.verify(codigo_totp):
            messagebox.showinfo(
                "¡Verificación Exitosa!",
                "Acceso concedido. Se ha completado la autenticación de dos factores correctamente."
            )
        else:
            messagebox.showerror(
                "Acceso Denegado",
                "El código TOTP ingresado es incorrecto o ha expirado."
            )


if __name__ == "__main__":
    args = parser.parse_args()
    if not args.basededatos.exists():
        print(f"Advertencia: No se encontró la base de datos en {args.basededatos}")
    
    root = tk.Tk()
    app = MFA(root, args.basededatos)
    root.mainloop()