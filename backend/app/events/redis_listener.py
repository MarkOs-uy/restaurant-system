import asyncio
import json

from app.core.redis import redis_client
from app.websocket.manager import manager
from backend.app.services.event_service import INSTANCE_ID


async def redis_event_listener():

    pubsub = redis_client.pubsub()

    await pubsub.subscribe("restaurant_events")

    print("Redis listener started")

    try:
        async for message in pubsub.listen():

            if message["type"] != "message":
                continue

            data = json.loads(message["data"])

            # evitar duplicados
            if data.get("origin") == INSTANCE_ID:
                continue

            restaurant_id = data.get("restaurant_id")
            target = data.get("target")
            target_id = data.get("target_id")

            if target == "broadcast":
                await manager.broadcast(restaurant_id, data)

            elif target == "role":
                await manager.send_to_role(restaurant_id, target_id, data)

            elif target == "station":
                await manager.send_to_station(restaurant_id, target_id, data)

    except asyncio.CancelledError:
        print("Redis listener stopped")

    finally:
        await pubsub.unsubscribe("restaurant_events")
        await pubsub.close()