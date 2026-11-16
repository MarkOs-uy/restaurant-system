import socket


class NetworkPrinter:
    def __init__(
        self,
        host: str,
        port: int = 9100,
        timeout: float = 3.0,
    ):
        self.host = host
        self.port = port
        self.timeout = timeout

    def _send(self, data: bytes) -> None:
        with socket.create_connection(
            (self.host, self.port),
            timeout=self.timeout,
        ) as sock:
            sock.sendall(data)

    def print_text(
        self,
        text: str,
        cut: bool = True,
    ) -> None:
        ESC_INIT = b"\x1b\x40"
        FEED_LINES = b"\x1b\x64\x05"
        CUT_FULL = b"\x1d\x56\x00"

        payload = bytearray()

        # Inicializar impresora
        payload.extend(ESC_INIT)

        # Texto
        payload.extend(
            text.encode(
                "cp850",
                errors="replace",
            )
        )

        # Asegurar salto de línea final
        if not text.endswith("\n"):
            payload.extend(b"\n")

        # Avanzar papel antes de cortar
        payload.extend(FEED_LINES)

        if cut:
            payload.extend(CUT_FULL)

        self._send(bytes(payload))