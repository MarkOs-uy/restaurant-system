from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.websocket.manager import manager
from app.db.session import SessionLocal
from app.dependencies.auth import AuthError, authenticate_token


router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    db: Session = SessionLocal()

    try:

        try:
            auth_user = authenticate_token(db, token)
        except AuthError:
            await websocket.close(code=1008)
            return

        station_id_param = websocket.query_params.get("station_id")

        try:
            station_id = int(station_id_param) if station_id_param else None
        except ValueError:
            station_id = None

        connected = await manager.connect(
            websocket,
            auth_user,
            station_id
        )

        if not connected:
            return

        try:

            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:

            manager.disconnect(websocket)

    finally:

        db.close()
