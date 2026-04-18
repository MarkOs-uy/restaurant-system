#!/usr/bin/env python3
"""
POS Zeroconf announcer
Anuncia los servicios del POS en la red local.

Servicios publicados:
- _pos._tcp.local  → descubrimiento del POS
- _http._tcp.local → acceso web
- _ws._tcp.local   → websocket
"""

import socket
import time
import signal
import sys
from zeroconf import Zeroconf, ServiceInfo


def get_local_ip():
    """Obtiene la IP local de la máquina"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def create_service(service_type, name, port, ip):
    return ServiceInfo(
        service_type,
        f"{name}.{service_type}",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={
            "version": "1.0",
            "service": name
        },
        server="pos.local."
    )


def main():

    ip = get_local_ip()

    print("POS Zeroconf announcer")
    print("IP detectada:", ip)

    zeroconf = Zeroconf()

    services = [

        create_service(
            "_pos._tcp.local.",
            "restaurant-pos",
            80,
            ip
        ),

        create_service(
            "_http._tcp.local.",
            "restaurant-pos-web",
            80,
            ip
        ),

        create_service(
            "_ws._tcp.local.",
            "restaurant-pos-ws",
            8000,
            ip
        )

    ]

    for service in services:
        zeroconf.register_service(service)
        print("Servicio publicado:", service.name)

    print("\nPOS disponible en:")
    print(f"http://pos.local")
    print(f"http://{ip}")

    print("\nCtrl+C para detener")

    def shutdown(sig, frame):
        print("\nCerrando Zeroconf...")
        for service in services:
            zeroconf.unregister_service(service)
        zeroconf.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()