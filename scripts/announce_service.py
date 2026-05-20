#!/usr/bin/env python3
"""
POS Zeroconf announcer.

Publishes the POS services on the local network so phones/tablets can discover
the server. The hostname itself (pos.local by default) is provided by Avahi on
the Linux host; this script publishes service metadata and ports.
"""

import os
import signal
import socket
import sys
import time

from zeroconf import ServiceInfo, Zeroconf


HOSTNAME = os.getenv("POS_HOSTNAME", "pos.local").rstrip(".")
FRONTEND_PORT = int(os.getenv("POS_FRONTEND_PORT", "5173"))
BACKEND_PORT = int(os.getenv("POS_BACKEND_PORT", "8000"))
SERVICE_NAME = os.getenv("POS_SERVICE_NAME", "restaurant-pos")


def get_local_ip() -> str:
    """Return the LAN IP without requiring the destination to be reachable."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)


def create_service(service_type: str, name: str, port: int, ip: str) -> ServiceInfo:
    return ServiceInfo(
        service_type,
        f"{name}.{service_type}",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={
            "version": "1.0",
            "hostname": HOSTNAME,
            "service": name,
        },
        server=f"{HOSTNAME}.",
    )


def main() -> None:
    ip = get_local_ip()

    print("POS Zeroconf announcer")
    print("IP detectada:", ip)
    print("Hostname:", f"{HOSTNAME}.")

    zeroconf = Zeroconf()

    services = [
        create_service(
            "_pos._tcp.local.",
            SERVICE_NAME,
            FRONTEND_PORT,
            ip,
        ),
        create_service(
            "_http._tcp.local.",
            f"{SERVICE_NAME}-web",
            FRONTEND_PORT,
            ip,
        ),
        create_service(
            "_ws._tcp.local.",
            f"{SERVICE_NAME}-ws",
            BACKEND_PORT,
            ip,
        ),
    ]

    for service in services:
        zeroconf.register_service(service)
        print("Servicio publicado:", service.name, "puerto:", service.port)

    print("\nPOS disponible en:")
    print(f"http://{HOSTNAME}:{FRONTEND_PORT}")
    print(f"http://{ip}:{FRONTEND_PORT}")

    def shutdown(_sig, _frame) -> None:
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
