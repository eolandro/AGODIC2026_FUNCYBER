"""
Servidor web sencillo para el inicio de sesión (sin librerías extra).

Reutiliza las funciones de iniciarSesion.py (validar credenciales y registrar
asistencia) y sirve la página login.html, que debe estar en la misma carpeta.

Uso:
	poetry run python src/servidorWeb.py basedatos.sqlite3
Después abre http://127.0.0.1:8000 en el navegador.

"""

import argparse
import json
import sqlite3
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from iniciarSesion import validarCredenciales, registrarAsistencia, MAX_INTENTOS

PUERTO = 8000
BLOQUEO_SEG = 60
HTML = Path(__file__).with_name("login.html")

# Intentos fallidos por IP: {ip: [fallos, bloqueado_hasta]}
fallos = {}

parser = argparse.ArgumentParser(
	prog='servidorWeb',
	description='Inicio de sesión web con contraseña y código multifactor',
	epilog='Fundamentos de Cyber'
)

parser.add_argument('BaseDeDatos', type=Path)

class Handler(BaseHTTPRequestHandler):
	rutaDB = None

	def responder(self, codigo, cuerpo, tipo="application/json"):
		datos = cuerpo if isinstance(cuerpo, bytes) else json.dumps(cuerpo).encode("utf-8")
		self.send_response(codigo)
		self.send_header("Content-Type", f"{tipo}; charset=utf-8")
		self.send_header("Content-Length", str(len(datos)))
		self.send_header("Cache-Control", "no-store")
		self.end_headers()
		self.wfile.write(datos)

	def do_GET(self):
		if self.path in ("/", "/login.html"):
			self.responder(200, HTML.read_bytes(), "text/html")
		else:
			self.responder(404, {"ok": False, "mensaje": "No encontrado."})

	def do_POST(self):
		if self.path != "/login":
			return self.responder(404, {"ok": False, "mensaje": "No encontrado."})

		ip = self.client_address[0]
		ahora = time.time()
		intentos, bloqueadoHasta = fallos.get(ip, [0, 0])

		if bloqueadoHasta > ahora:
			espera = int(bloqueadoHasta - ahora) + 1
			return self.responder(429, {
				"ok": False, "espera": espera,
				"mensaje": f"Demasiados intentos. Espera {espera} s."
			})

		try:
			largo = int(self.headers.get("Content-Length", 0))
			datos = json.loads(self.rfile.read(min(largo, 4096)))
			NoEmpleado = str(datos.get("noEmpleado", "")).strip()
			PWD = str(datos.get("password", ""))
			# Sin verificación en dos pasos: codigo=None (solo contraseña)
			dosPasos = datos.get("dosPasos") is True
			codigo = str(datos.get("codigo", "")).replace(" ", "") if dosPasos else None
		except (ValueError, AttributeError):
			return self.responder(400, {"ok": False, "mensaje": "Solicitud inválida."})

		con = sqlite3.connect(str(self.rutaDB.resolve()))
		try:
			usuario = validarCredenciales(con, NoEmpleado, PWD, codigo)
			if usuario is not None:
				fallos.pop(ip, None)
				idUsuario, Nombre = usuario
				FechaHora = registrarAsistencia(con, idUsuario)
				return self.responder(200, {"ok": True, "nombre": Nombre, "fechaHora": FechaHora, "dosPasos": dosPasos})
		finally:
			con.close()

		intentos += 1
		if intentos >= MAX_INTENTOS:
			fallos[ip] = [0, ahora + BLOQUEO_SEG]
			return self.responder(429, {
				"ok": False, "espera": BLOQUEO_SEG,
				"mensaje": "Demasiados intentos fallidos. Acceso bloqueado temporalmente."
			})

		fallos[ip] = [intentos, 0]
		self.responder(401, {
			"ok": False,
			"mensaje": "Número de empleado, contraseña o código incorrectos.",
			"restantes": MAX_INTENTOS - intentos
		})

if __name__ == "__main__":
	argumentos = parser.parse_args()
	if not argumentos.BaseDeDatos.exists():
		print("\nNo se encontró la DB.")
	else:
		Handler.rutaDB = argumentos.BaseDeDatos
		servidor = HTTPServer(("127.0.0.1", PUERTO), Handler)
		print(f"Servidor listo en http://127.0.0.1:{PUERTO}  (Ctrl+C para detener)")
		try:
			servidor.serve_forever()
		except KeyboardInterrupt:
			print("\nServidor detenido.")
		finally:
			servidor.server_close()
