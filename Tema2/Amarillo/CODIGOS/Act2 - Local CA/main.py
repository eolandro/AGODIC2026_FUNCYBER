import os
import ssl
from bottle import route, run, template, ServerAdapter

BASE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.join(BASE, "santavaca.pem")
KEY = os.path.join(BASE, "santavaca-key.pem")
CHAIN = os.path.join(BASE, "rootCA.pem")


class SSLCherootAdapter(ServerAdapter):
    def run(self, handler):
        from cheroot import wsgi
        from cheroot.ssl.builtin import BuiltinSSLAdapter

        server = wsgi.Server((self.host, self.port), handler)
        server.ssl_adapter = BuiltinSSLAdapter(CERT, KEY, CHAIN)

        server.ssl_adapter.context.options |= ssl.OP_NO_TLSv1
        server.ssl_adapter.context.options |= ssl.OP_NO_TLSv1_1

        try:
            server.start()
        finally:
            server.stop()


@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>! (servidor: santavaca.corral)', name=name)


run(host='0.0.0.0', port=8080, server=SSLCherootAdapter)
