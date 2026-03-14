from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager

router = APIRouter()

@router.websocket("/ws/waiter/{restaurant_id}")
async def waiter_ws(websocket: WebSocket, restaurant_id: int):

    await manager.connect_waiter(websocket, restaurant_id)

    try:
        while True:
            await websocket.receive()

    except WebSocketDisconnect:
        manager.disconnect_waiter(websocket, restaurant_id)