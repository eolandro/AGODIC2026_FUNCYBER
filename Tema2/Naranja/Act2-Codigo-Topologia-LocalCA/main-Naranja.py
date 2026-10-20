from bottle import route, run, template,ServerAdapter

class SSLCherootAdapter(ServerAdapter):
    def run(self, handler):
        from cheroot import wsgi
        from cheroot.ssl.builtin import BuiltinSSLAdapter
        import ssl

        server = wsgi.Server((self.host, self.port), handler)
        server.ssl_adapter = BuiltinSSLAdapter(
            r"src/naranja+1.pem",
            r"src/naranja+1-key.pem"
            r"src/naranja1+1.pem",
            r"src/naranja1+1-key.pem"
            r"src/naranja2+1.pem",
            r"src/naranja2+1-key.pem")

        # By default, the server will allow negotiations with extremely old protocols
        # that are susceptible to attacks, so we only allow TLSv1.2
        server.ssl_adapter.context.options |= ssl.OP_NO_TLSv1
        server.ssl_adapter.context.options |= ssl.OP_NO_TLSv1_1

        try:
            server.start()
        finally:
            server.stop()

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

run(host='localhost', port=8080, server='SSLCherootAdapter')