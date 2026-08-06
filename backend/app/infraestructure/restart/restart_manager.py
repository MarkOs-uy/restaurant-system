import threading
import time
import os


class RestartManager:

    _requested = False
    _lock = threading.Lock()

    @classmethod
    def request_restart(cls):

        with cls._lock:
            if cls._requested:
                return
            cls._requested = True

        threading.Thread(
            target=cls._restart,
            daemon=True
        ).start()


    @staticmethod
    def _restart():
        time.sleep(3)
        print(os.getpid())
        os._exit(0)