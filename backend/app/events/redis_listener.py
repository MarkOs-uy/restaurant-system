import asyncio
import json
import logging

from app.core.redis import redis_client
from app.websocket.manager import manager
from app.services.event_worker import INSTANCE_ID
from app.models.user import UserRole

logger = logging.getLogger("app.redis_listener")

CHANNEL = "restaurant_events"


async def _process_event(data: dict):
    try:

        # ignorar eventos propios
        if data.get("origin") == INSTANCE_ID:
            return

        restaurant_id = data.get("restaurant_id")
        target = data.get("target")
        target_id = data.get("target_id")
        event_type = data.get("event_type")
        payload = data.get("payload") or {}

        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                logger.warning("Invalid JSON payload: %s", payload)
                return

        if not restaurant_id or not event_type:
            logger.warning("Invalid event received: %s", data)
            return

        if not isinstance(payload, dict):
            logger.warning("Invalid payload type: %s", type(payload))
            return

        message = {
            "type": event_type,
            "data": payload
        }

        logger.debug(
            "Dispatch WS event: r=%s target=%s type=%s payload=%s",
            restaurant_id,
            target,
            event_type,
            payload
        )

        if target == "broadcast":

            await manager.broadcast(
                restaurant_id,
                message
            )

        elif target == "role":

            await manager.send_to_role(
                restaurant_id,
                UserRole(target_id),
                message
            )

        elif target == "station":

            await manager.send_to_station(
                restaurant_id,
                int(target_id),
                message
            )

        else:

            logger.warning(
                "Unknown event target: %s",
                target
            )

    except Exception:
        logger.exception("Error processing redis event")


async def redis_event_listener():

    while True:

        pubsub = None

        try:

            logger.info("Starting Redis listener")

            pubsub = redis_client.pubsub()

            await pubsub.subscribe(CHANNEL)

            logger.info("Subscribed to %s", CHANNEL)

            async for message in pubsub.listen():

                try:

                    if message["type"] != "message":
                        continue

                    raw = message["data"]

                    if not raw:
                        continue

                    # Redis puede enviar bytes
                    if isinstance(raw, bytes):
                        raw = raw.decode()

                    data = json.loads(raw)

                    # procesar evento sin bloquear listener
                    asyncio.create_task(
                        _process_event(data)
                    )

                except Exception:
                    logger.exception("Error reading redis message")

        except asyncio.CancelledError:

            logger.info("Redis listener cancelled")
            break

        except Exception:

            logger.exception(
                "Redis listener crashed. Reconnecting in 3 seconds..."
            )

            await asyncio.sleep(3)

        finally:

            if pubsub:

                try:
                    await pubsub.unsubscribe(CHANNEL)
                    await pubsub.close()
                except Exception:
                    pass

            logger.info("Redis listener stopped")