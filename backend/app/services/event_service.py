# backend/app/domain/event_service.py

import asyncio
import json
import logging
import uuid
from sqlalchemy.orm import Session

from app.websocket.manager import manager
from app.models.user import UserRole
from app.models.domain_event import DomainEvent
from app.db.session import SessionLocal
from app.core.redis import redis_client

logger = logging.getLogger(__name__)
INSTANCE_ID = str(uuid.uuid4())

class EventService:

    # =========================
    # API PÚBLICA
    # =========================

    def __init__(self):
        self.loop = None


    def emit_to_role(self, restaurant_id: int, role: UserRole, message: dict):
        print("EVENT emit_to_role", message)
        event = {
            "restaurant_id": restaurant_id,
            "target": "role",
            "target_id": role.value if hasattr(role, "value") else role,
            "origin": INSTANCE_ID,
            "payload": message,
            "type": message.get("type")
        }
        self._persist_event(restaurant_id, event)
        self._dispatch(manager.send_to_role, restaurant_id, role, message)

    def emit_to_station(self, restaurant_id: int, station_id: int, message: dict):
        print("EVENT emit_to_station", message)
        event = {
            "restaurant_id": restaurant_id,
            "target": "station",
            "target_id": station_id,
            "origin": INSTANCE_ID,
            "payload": message,
            "type": message.get("type")
        }
        self._persist_event(restaurant_id, event)
        self._dispatch(manager.send_to_station, restaurant_id, station_id, message)

    def broadcast(self, restaurant_id: int, message: dict):
        print("EVENT broadcast", message)
        event = {
            "restaurant_id": restaurant_id,
            "target": "broadcast",
            "origin": INSTANCE_ID,
            "payload": message,
            "type": message.get("type")
        }
        self._persist_event(restaurant_id, event)
        self._dispatch(manager.broadcast, restaurant_id, message)

    # =========================
    # PERSISTENCIA
    # =========================

    def _persist_event(self, restaurant_id: int, event: dict):
        db = SessionLocal()
        try:
            event = DomainEvent(
                restaurant_id=restaurant_id,
                event_type=event.get("type"),
                payload=event
            )
            db.add(event)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error("Error persistiendo evento: %s", e)
        finally:
            db.close()

    # =========================
    # DESPACHO
    # =========================

    def _dispatch(self, func, *args):
        """
        Agenda las coroutines en el loop de FastAPI.
        Guarda referencia a cada tarea para evitar garbage collection
        y registra errores en el callback.
        """
        logger.info("emit event type=%s", args[-1].get("type"))
        try:
            loop = self.loop
            if not loop:
                logger.error("Event loop not initialized")
                return
        except RuntimeError:
            # Nunca debería ocurrir en FastAPI, pero por seguridad:
            logger.error("_dispatch llamado fuera de un loop async. Evento descartado.")
            return

        event = args[-1]

        self._create_task(loop, func(*args))
        self._create_task(loop, self._publish_redis(event))


    def _create_task(self, loop: asyncio.AbstractEventLoop, coro):
        """
        Crea la tarea guardando referencia y registrando errores.
        """
        task = loop.create_task(coro)

        # Guardar referencia evita que el GC la elimine antes de completar
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)
        task.add_done_callback(_log_task_error)

    # =========================
    # REDIS
    # =========================

    async def _publish_redis(self, message: dict):
        try:
            await redis_client.publish(
                "restaurant_events",
                json.dumps(message)
            )
        except Exception as e:
            logger.error("Error publicando en Redis: %s", e)


# Set global para mantener referencias a tareas en vuelo
# Evita que el GC las elimine antes de que completen
_background_tasks: set[asyncio.Task] = set()


def _log_task_error(task: asyncio.Task):
    """Callback que registra excepciones de tareas background."""
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        logger.error(
            "Error en tarea background [%s]: %s",
            task.get_name(),
            exc,
            exc_info=exc
        )


event_service = EventService()