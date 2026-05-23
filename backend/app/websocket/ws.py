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

        connected = await manager.connect(
            websocket,
            auth_user
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
