from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.websocket.manager import manager
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User, UserRole


router = APIRouter()


class AuthUser:

    def __init__(self, user: User):

        self.id = user.id
        self.role = user.role
        self.restaurant_id = user.restaurant_id


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

    user_id = payload.get("sub")
    restaurant_id = payload.get("restaurant_id")
    role = payload.get("role")

    if not user_id or not restaurant_id or not role:
        await websocket.close(code=1008)
        return

    db: Session = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.id == user_id,
                User.restaurant_id == restaurant_id,
                User.active == True
            )
            .first()
        )

        if not user:
            await websocket.close(code=1008)
            return

        try:
            user_role = UserRole(role)
        except ValueError:
            await websocket.close(code=1008)
            return

        if user.role != user_role:
            await websocket.close(code=1008)
            return

        station_id_param = websocket.query_params.get("station_id")

        try:
            station_id = int(station_id_param) if station_id_param else None
        except ValueError:
            station_id = None

        auth_user = AuthUser(user)

        await manager.connect(
            websocket,
            auth_user,
            station_id
        )

        try:

            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:

            manager.disconnect(websocket)

    finally:

        db.close()