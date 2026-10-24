from bottle import route, run, template, ServerAdapter

class SSLCherootAdapter(ServerAdapter):
    def run(self, handler):
        from cheroot import wsgi
        from cheroot.ssl.builtin import BuiltinSSLAdapter
        import ssl

        server = wsgi.Server((self.host, self.port), handler)
        server.ssl_adapter = BuiltinSSLAdapter("cerceta1.cerceta.local.pem", "cerceta1.cerceta.local-key.pem")
        server.ssl_adapter.context.minimum_version = ssl.TLSVersion.TLSv1_2

        try:
            server.start()
        finally:
            server.stop()

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

run(host='0.0.0.0', port=8080, server=SSLCherootAdapter)
