from dnslib.server import DNSServer, BaseResolver
from dnslib import RR, A, QTYPE
from numpy import rint

TABLA_DNS = {
    "ladrillo1.lab.": "192.168.0.178",
    "ladrillo2.lab.": "192.168.0.181",
    "servidor.lab.": "192.168.0.124"
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
        # Responde con 192.168.42.10 a cualquier consulta que reciba


        return reply

resolver = LabResolver()
# 0.0.0.0 permite escuchar en cualquier interfaz de red disponible
server = DNSServer(resolver, port=53, address="0.0.0.0")
print("Servidor DNS activo en el puerto 53 (0.0.0.0)...")
try:
    server.start()
except KeyboardInterrupt:
    server.stop()