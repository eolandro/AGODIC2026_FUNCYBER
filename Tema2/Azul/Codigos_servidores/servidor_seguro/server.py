import http.server
import ssl
import os
IP_ESCUCHA = "0.0.0.0"
PUERTO = 443
DIRECTORIO_WEB = "public"
class HTTPServerConDirectorio(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORIO_WEB, **kwargs)
def iniciar_servidor():
    server_address = (IP_ESCUCHA, PUERTO)
    httpd = http.server.HTTPServer(server_address, HTTPServerConDirectorio)
    cert_file = os.path.join("certs", "webserver1.local.pem")
    key_file = os.path.join("certs", "webserver1.local-key.pem")
    contexto_ssl = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    contexto_ssl.load_cert_chain(certfile=cert_file, keyfile=key_file)
    httpd.socket = contexto_ssl.wrap_socket(httpd.socket, server_side=True)
    print(f"🚀 Servidor HTTPS en linea...")
    print(f"🌍 URL OBLIGATORIA: https://webserver1.local")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido.")
if __name__ == "__main__":
    iniciar_servidor()