from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/kitchen/{restaurant_id}/{station_id}")
async def kitchen_ws(websocket: WebSocket, restaurant_id: int, station_id: int):

    await manager.connect(websocket, restaurant_id, station_id)

    try:
        while True:

            message = await websocket.receive()

            # si el cliente se desconecta
            if message["type"] == "websocket.disconnect":
                break

            # si llega texto (no lo usamos, pero lo aceptamos)
            if message["type"] == "websocket.receive":
                pass

    except WebSocketDisconnect:
        pass

    finally:

        manager.disconnect(websocket, restaurant_id, station_id)

        print(
            "Kitchen clients:",
            len(manager.connections[restaurant_id][station_id])
        )