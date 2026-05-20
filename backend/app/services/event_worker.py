import asyncio
import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.event_outbox import EventOutbox
from app.websocket.manager import manager
from app.core.redis import redis_client
from app.models.user import UserRole

import uuid

INSTANCE_ID = str(uuid.uuid4())

logger = logging.getLogger("app.event_worker")


# =========================
# CONFIGURACIÓN
# =========================

POLL_INTERVAL = 0.5
MAX_RETRIES = 6
BASE_RETRY_DELAY = 2
BATCH_SIZE = 50
EVENT_TTL_HOURS = 48


# =========================
# WORKER PRINCIPAL
# =========================

class EventWorker:

    async def run(self):

        logger.info("EventWorker started")

        while True:

            try:
                await self._process_batch()

            except Exception as e:
                logger.exception("EventWorker loop error: %s", e)

            await asyncio.sleep(POLL_INTERVAL)

    # =========================
    # PROCESAR EVENTOS
    # =========================

    async def _process_batch(self):

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
                return

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

    # =========================
    # ENTREGA DEL EVENTO
    # =========================

    async def _deliver_event(self, event: EventOutbox):

        payload = event.payload or {}

        message = {
            "type": event.event_type,
            "payload": event.payload
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

            await manager.send_to_station(
                event.restaurant_id,
                int(event.target_id),
                message
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