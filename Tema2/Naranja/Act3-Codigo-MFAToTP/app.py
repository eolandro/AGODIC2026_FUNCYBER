import sqlite3
import bcrypt
import pyotp
from flask import Flask, render_template_string, request

app = Flask(__name__)

def cargar_html():
    with open("src/login.html", "r", encoding="utf-8") as f:
        return f.read()

@app.route('/')
def index():
    return render_template_string(cargar_html())

@app.route('/login', methods=['POST'])
def login():
    num_empleado = request.form.get('num_empleado')
    contrasena = request.form.get('contrasena')
    codigo_qr = request.form.get('codigo_qr')

    conn = sqlite3.connect('BaseSQLite.db')
    cursor = conn.cursor()

    # Obtener el nombre de la tabla omitiendo tablas internas de SQLite
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tablas = cursor.fetchall()
    
    if not tablas:
        conn.close()
        return "Error: No hay tablas en la base de datos."

    nombre_tabla = tablas[0][0]

    # Consultar id, NoEmpleado, Nombre, hash y Semilla
    cursor.execute(f"SELECT id, NoEmpleado, Nombre, hash, Semilla FROM {nombre_tabla} WHERE NoEmpleado = ?", (num_empleado,))
    usuario = cursor.fetchone()

    if usuario:
        hash_guardado = usuario[3]      # Columna 'hash'
        semilla_guardada = usuario[4]   # Columna 'Semilla'
        
        es_valido = False

        # Validación 1: Por contraseña 
        if contrasena and bcrypt.checkpw(contrasena.encode('utf-8'), hash_guardado.encode('utf-8')):
            es_valido = True

        # Validación 2: Por código de 6 dígitos del Authenticator 
        if codigo_qr and semilla_guardada and pyotp.TOTP(semilla_guardada).verify(codigo_qr):
            es_valido = True

        if es_valido:
            nombre_usuario = usuario[2]  # Columna 'Nombre'
            cursor.execute("INSERT INTO asistencia (idusuario, fechahora) VALUES (?, datetime('now', 'localtime'))", (usuario[0],))
            conn.commit()
            conn.close()
            
            # Pantalla de éxito con el botón "Salir"
            return f'''
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Inicio Exitoso</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f0f2f5;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }}
                    .card {{
                        background-color: #ffffff;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                        text-align: center;
                        width: 100%;
                        max-width: 350px;
                    }}
                    h1 {{
                        color: #333;
                        font-size: 22px;
                        margin-bottom: 10px;
                    }}
                    p {{
                        color: #666;
                        margin-bottom: 25px;
                    }}
                    .btn-salir {{
                        display: inline-block;
                        padding: 10px 24px;
                        background-color: #dc3545;
                        color: white;
                        text-decoration: none;
                        border-radius: 4px;
                        font-weight: bold;
                        transition: background 0.2s;
                    }}
                    .btn-salir:hover {{
                        background-color: #c82333;
                    }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>¡Bienvenido/a, {nombre_usuario}!</h1>
                    <p>Has iniciado sesión correctamente.</p>
                    <a href="/" class="btn-salir">Salir</a>
                </div>
            </body>
            </html>
            '''
        else:
            return "<h1>Error:</h1><p>Contraseña o código de autenticación incorrecto.</p><a href='/'>Volver a intentar</a>"
    else:
        return "<h1>Error:</h1><p>Número de empleado no encontrado.</p><a href='/'>Volver a intentar</a>"

if __name__ == '__main__':
    app.run(debug=True)