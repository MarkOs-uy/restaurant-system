from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.domain.errors.base import DomainError
from app.dependencies.auth import authenticate_token
from app.websocket.manager import manager

router = APIRouter()


# --------------------------------------------------------------------------------------
# Establece una conexión WebSocket autenticada mediante un token JWT.
# --------------------------------------------------------------------------------------
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    db: Session = SessionLocal()

    try:

        try:
            auth_user = authenticate_token(db, token)
        except DomainError:
            await websocket.close(code=1008)
            return

        connected = await manager.connect(
            websocket,
            auth_user,
        )

        if not connected:
            return

        try:
            # Mantener la conexión abierta mientras el cliente permanezca conectado.
            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            manager.disconnect(websocket)

    finally:
        db.close()