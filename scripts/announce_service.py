#!/usr/bin/env python3
"""
Anuncia el servidor POS en la red local via mDNS/Zeroconf.
Debe correr en el HOST, fuera de Docker.
"""
import socket
import time
import signal
import sys
from zeroconf import Zeroconf, ServiceInfo


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def main():
    ip = get_local_ip()
    port = 8000

    info = ServiceInfo(
        "_pos._tcp.local.",
        "restaurant-pos._pos._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={"version": "1.0"}
    )

    zc = Zeroconf()
    zc.register_service(info)
    print(f"[Zeroconf] POS disponible en http://{ip}:{port}")
    print("[Zeroconf] Ctrl+C para detener")

    def shutdown(sig, frame):
        print("\n[Zeroconf] Cerrando...")
        zc.unregister_service(info)
        zc.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()