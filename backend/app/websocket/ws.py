from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager
from app.core.security import decode_access_token

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    payload = decode_access_token(token)

    if not payload:
        await websocket.close(code=1008)
        return

    # 🔥 ARMAR USER FAKE (simple y suficiente)
    class WSUser:
        def __init__(self, payload):
            self.id = payload.get("sub")
            self.role = payload.get("role")
            self.restaurant_id = payload.get("restaurant_id")

    user = WSUser(payload)

    station_id = websocket.query_params.get("station_id")

    await manager.connect(
        websocket,
        user,
        int(station_id) if station_id else None
    )

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)