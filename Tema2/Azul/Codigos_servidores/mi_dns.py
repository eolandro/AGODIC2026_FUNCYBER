from dnslib.server import DNSServer, BaseResolver
from dnslib import RR, A, QTYPE
from numpy import rint

TABLA_DNS = {
    "webserver1.local.": "192.168.1.105",
    "webserver2.local.": "192.168.1.236",
    "servidordns": "192.168.1.85"
}

class LabResolver(BaseResolver):
    def resolve(self, request, handler):
        reply = request.reply()
        qname = str(request.q.qname).lower()

        if qname in TABLA_DNS:
            ip_resp = TABLA_DNS[qname]
            reply.add_answer(RR(qname, QTYPE.A, rdata=A(ip_resp), ttl=60))
            print(f"[*] Resuelto: {qname.strip('.')} -> {ip_resp}")
        else:
            print(f"[-] no encontrado: {qname.strip('.')}")
       


        return reply

resolver = LabResolver()
server = DNSServer(resolver, port=53, address="0.0.0.0")
print("Servidor DNS activo en el puerto 53 (0.0.0.0)...")
try:
    server.start()
except KeyboardInterrupt:
    server.stop()