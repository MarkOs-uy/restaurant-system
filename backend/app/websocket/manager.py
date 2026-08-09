import logging

from fastapi import WebSocket
from collections import defaultdict
from typing import Any

from app.models.user import User, UserRole


logger = logging.getLogger("app.websocket.manager")

MAX_CONNECTIONS_PER_USER = 3


class ConnectionManager:
    """
    Administra las conexiones WebSocket activas.

    Mantiene índices por restaurante, rol y usuario para facilitar
    el envío eficiente de mensajes.
    """

    def __init__(self) -> None:
        # websocket_id -> connection
        self._ws_index: dict[int, dict[str, Any]] = {}

        # restaurant -> connections
        self._by_restaurant: defaultdict[int, set[int]] = defaultdict(set)

        # restaurant -> role -> connections
        self._by_role: defaultdict[int, defaultdict[UserRole, set[int]]] = \
            defaultdict(lambda: defaultdict(set))

        # user -> connection_count
        self._user_connections: defaultdict[int, int] = defaultdict(int)

# --------------------------------------------------------------------------------------
# Acepta una nueva conexión WebSocket autenticada.
# --------------------------------------------------------------------------------------
    async def connect(self, websocket: WebSocket, user: User,) -> bool:

        if self._user_connections[user.id] >= MAX_CONNECTIONS_PER_USER:
            logger.warning(
                "WS rejected user=%s reason=max_connections",
                user.id
            )
            await websocket.close(code=1008)
            return False

        await websocket.accept()

        conn = {
            "ws": websocket,
            "user": user
        }

        ws_id = id(websocket)

        self._ws_index[ws_id] = conn
        self._by_restaurant[user.restaurant_id].add(ws_id)
        self._by_role[user.restaurant_id][user.role].add(ws_id)

        self._user_connections[user.id] += 1

        logger.info(
            "WS connected r=%s user=%s role=%s",
            user.restaurant_id,
            user.id,
            user.role
        )

        return True

# --------------------------------------------------------------------------------------
# Elimina una conexión WebSocket.
# --------------------------------------------------------------------------------------
    def disconnect(self, websocket: WebSocket):

        ws_id = id(websocket)

        conn = self._ws_index.pop(ws_id, None)

        if not conn:
            return

        user = conn["user"]
        restaurant_id = user.restaurant_id

        self._by_restaurant[restaurant_id].discard(ws_id)

        self._by_role[restaurant_id][user.role].discard(ws_id)

        self._user_connections[user.id] -= 1

        if self._user_connections[user.id] <= 0:
            del self._user_connections[user.id]

        logger.info(
            "WS disconnected r=%s user=%s",
            restaurant_id,
            user.id
        )

# --------------------------------------------------------------------------------------
# Envía un mensaje a todos los usuarios de un rol.
# --------------------------------------------------------------------------------------
    async def send_to_role(
        self,
        restaurant_id: int,
        role: UserRole,
        message: dict
    ):

        targets = list(self._by_role[restaurant_id].get(role, []))

        if not targets:
            logger.warning(
                "WS role send: no targets restaurant=%s role=%s message=%s",
                restaurant_id,
                role,
                message["type"]
            )
            return

        logger.debug("WS role send: r=%s role=%s connections=%s", restaurant_id, role, len(targets))
        for ws_id in targets:
            await self._safe_send(ws_id, message)

# --------------------------------------------------------------------------------------
# Envía un mensaje a todos los usuarios.
# --------------------------------------------------------------------------------------
    async def broadcast(
        self,
        restaurant_id: int,
        message: dict
    ):
        targets = list(self._by_restaurant.get(restaurant_id, []))
        logger.debug("WS broadcast: r=%s connections=%s", restaurant_id, len(targets))
        for ws_id in targets:
            await self._safe_send(ws_id, message)

# --------------------------------------------------------------------------------------
# Envía un mensaje
# --------------------------------------------------------------------------------------
    async def _safe_send(self, ws_id: int, message: dict):
        conn = self._ws_index.get(ws_id)
        if not conn:
            return
        ws = conn["ws"]
        try:
            logger.info("WS send: ws_id=%s type=%s", ws_id, message["type"])
            await ws.send_json(message)
        except Exception:
            logger.exception("WS send failed ws_id=%s", ws_id,)
            self.disconnect(ws)


manager = ConnectionManager()
