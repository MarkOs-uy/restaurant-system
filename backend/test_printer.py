from app.infrastructure.printing.network_printer import NetworkPrinter


printer = NetworkPrinter(
    host="192.168.1.151",
    port=9100,
)

printer.print_text(
    """
MARCHA - PRUEBA PYTHON

Servidor Debian OK
NetworkPrinter OK
Impresion ESC/POS OK
"""
)