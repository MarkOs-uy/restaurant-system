import asyncio
from app.websocket.manager import manager


class EventService:

    def __init__(self):
        pass

    # =========================
    # CORE
    # =========================

    def emit_to_role(self, restaurant_id: int, role: str, message: dict):
        self._dispatch(manager.send_to_role, restaurant_id, role, message)

    def emit_to_station(self, restaurant_id: int, station_id: int, message: dict):
        self._dispatch(manager.send_to_station, restaurant_id, station_id, message)

    def broadcast(self, restaurant_id: int, message: dict):
        self._dispatch(manager.broadcast, restaurant_id, message)

    # =========================
    # INTERNAL
    # =========================

    def _dispatch(self, func, *args):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(func(*args))
        except RuntimeError:
            # fallback si no hay loop activo (sync context)
            asyncio.run(func(*args))


event_service = EventService()