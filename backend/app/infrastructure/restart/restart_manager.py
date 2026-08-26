import os
import threading
import time


class RestartManager:
    """
    Gestiona el reinicio controlado del proceso de la aplicación.

    Se utiliza principalmente después de solicitar la restauración de un backup,
    permitiendo que la respuesta HTTP sea enviada antes de finalizar el proceso.
    """

    _requested: bool = False
    _lock = threading.Lock()

    # --------------------------------------------------------------------------------------
    # Solicita el reinicio de la aplicación.
    # Si ya existe una solicitud pendiente, no hace nada.
    # --------------------------------------------------------------------------------------
    @classmethod
    def request_restart(cls) -> None:

        with cls._lock:

            if cls._requested:
                return

            cls._requested = True

        threading.Thread(
            target=cls._restart,
            daemon=True,
        ).start()

    # --------------------------------------------------------------------------------------
    # Espera unos segundos para permitir que la respuesta HTTP llegue al cliente
    # y luego finaliza el proceso. Docker o el supervisor correspondiente se
    # encargará de iniciarlo nuevamente.
    # --------------------------------------------------------------------------------------
    @staticmethod
    def _restart() -> None:

        time.sleep(3)

        os._exit(0)