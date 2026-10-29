import http.server
import ssl

PORT = 443
server_address = ('0.0.0.0', PORT)

# Configurar el servidor HTTP básico
httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)

# Configurar el contexto SSL usando las llaves de mkcert
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# Certificado y llave
context.load_cert_chain(certfile='ladrillo1.lab+1.pem', keyfile='ladrillo1.lab+1-key.pem')

# Envolver el socket con SSL para que sea HTTPS
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print(f"[*] Servidor HTTPS seguro corriendo en https://ladrillo1.lab")
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\n[!] Servidor detenido por el usuario.")
    httpd.server_close()