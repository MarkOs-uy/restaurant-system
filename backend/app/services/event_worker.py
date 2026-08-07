import asyncio
import json
import logging
import uuid

from datetime import datetime, timezone

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.websocket.manager import manager
from app.core.redis import redis_client

from app.models.user import UserRole
from app.models.event_outbox import EventOutbox


INSTANCE_ID = str(uuid.uuid4())

logger = logging.getLogger("app.event_worker")

# --------------------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------------------
POLL_INTERVAL = 0.5
BATCH_SIZE = 50

MAX_RETRIES = 6
BASE_RETRY_DELAY = 2

EVENT_TTL_HOURS = 48 # Utilizada por la tarea periódica que elimina eventos antiguos.


class EventWorker:
    """
    Procesa los eventos pendientes almacenados en la tabla EventOutbox.

    Su responsabilidad es:

    - entregar eventos a los clientes WebSocket locales;
    - replicarlos mediante Redis para otras instancias;
    - gestionar reintentos automáticos;
    - marcar los eventos como procesados o fallidos.
    """

# --------------------------------------------------------------------------------------
# Inicia el ciclo principal del EventWorker.
# --------------------------------------------------------------------------------------
    async def run(self) -> None:
        logger.info("EventWorker started")
        while True:
            try:
                await self._process_batch()
            except Exception:
                logger.exception("EventWorker loop error")
            await asyncio.sleep(POLL_INTERVAL)

# --------------------------------------------------------------------------------------
# Procesa un lote de eventos pendientes.
# --------------------------------------------------------------------------------------
    async def _process_batch(self) -> None:
        db: Session = SessionLocal()
        try:
            stmt = (
                select(EventOutbox)
                .where(EventOutbox.status == "pending")
                .order_by(EventOutbox.id)
                .limit(BATCH_SIZE)
                .with_for_update(skip_locked=True)
            )
            events = db.execute(stmt).scalars().all()
            if not events:
                return None
            for event in events:
                try:
                    await self._deliver_event(event)
                    event.status = "processed"
                    event.processed_at = datetime.now(timezone.utc)
                except Exception as e:
                    event.retries += 1
                    event.last_error = str(e)
                    if event.retries >= MAX_RETRIES:
                        event.status = "failed"
                        logger.error(
                            "Event failed permanently id=%s type=%s",
                            event.id,
                            event.event_type
                        )
                    else:
                        delay = BASE_RETRY_DELAY ** event.retries
                        logger.warning(
                            "Event retry id=%s attempt=%s delay=%ss",
                            event.id,
                            event.retries,
                            delay
                        )
                        await asyncio.sleep(delay)
                db.commit()
        finally:
            db.close()

# --------------------------------------------------------------------------------------
# Entrega un evento mediante WebSocket y lo replica en Redis.
# --------------------------------------------------------------------------------------
    async def _deliver_event(self, event: EventOutbox,) -> None:
        payload = event.payload or {}
        message = {
            "type": event.event_type,
            "payload": payload
        }
        # ---- websocket delivery ----
        if event.target == "broadcast":
            await manager.broadcast(
                event.restaurant_id,
                message
            )
        elif event.target == "role":
            await manager.send_to_role(
                event.restaurant_id,
                UserRole(event.target_id),
                message
            )
        elif event.target == "station":
            station_payload = {
                **payload,
                "station_id": int(event.target_id)
            }
            await manager.send_to_role(
                event.restaurant_id,
                UserRole.KITCHEN,
                {
                    "type": event.event_type,
                    "payload": station_payload
                }
            )

        # ---- redis replication ----

        await redis_client.publish(
            "restaurant_events",
            json.dumps({
                "origin": INSTANCE_ID,
                "restaurant_id": event.restaurant_id,
                "event_type": event.event_type,
                "payload": payload,
                "target": event.target,
                "target_id": event.target_id
            })
        )
