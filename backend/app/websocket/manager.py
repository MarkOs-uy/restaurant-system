from fastapi import WebSocket
from collections import defaultdict
from app.models.user import UserRole
import logging

logger = logging.getLogger("app.websocket.manager")

MAX_CONNECTIONS_PER_USER = 3


class ConnectionManager:

    def __init__(self):

        # websocket_id -> connection
        self._ws_index = {}

        # restaurant -> connections
        self._by_restaurant = defaultdict(set)

        # restaurant -> role -> connections
        self._by_role = defaultdict(lambda: defaultdict(set))

        # restaurant -> station -> connections
        self._by_station = defaultdict(lambda: defaultdict(set))

        # user -> connection_count
        self._user_connections = defaultdict(int)

    # =========================
    # CONNECT
    # =========================

    async def connect(self, websocket: WebSocket, user, station_id=None):

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
            "user": user,
            "station_id": station_id
        }

        ws_id = id(websocket)

        self._ws_index[ws_id] = conn
        self._by_restaurant[user.restaurant_id].add(ws_id)
        self._by_role[user.restaurant_id][user.role].add(ws_id)

        if station_id:
            self._by_station[user.restaurant_id][station_id].add(ws_id)

        self._user_connections[user.id] += 1

        logger.info(
            "WS connected r=%s user=%s role=%s station=%s",
            user.restaurant_id,
            user.id,
            user.role,
            station_id
        )

        return True

    # =========================
    # DISCONNECT
    # =========================

    def disconnect(self, websocket: WebSocket):

        ws_id = id(websocket)

        conn = self._ws_index.pop(ws_id, None)

        if not conn:
            return

        user = conn["user"]
        restaurant_id = user.restaurant_id
        station_id = conn["station_id"]

        self._by_restaurant[restaurant_id].discard(ws_id)

        self._by_role[restaurant_id][user.role].discard(ws_id)

        if station_id:
            self._by_station[restaurant_id][station_id].discard(ws_id)

        self._user_connections[user.id] -= 1

        if self._user_connections[user.id] <= 0:
            del self._user_connections[user.id]

        logger.info(
            "WS disconnected r=%s user=%s",
            restaurant_id,
            user.id
        )

    # =========================
    # SENDS
    # =========================

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


    async def send_to_station(
        self,
        restaurant_id: int,
        station_id: int,
        message: dict
    ):

        targets = list(self._by_station[restaurant_id].get(station_id, []))
        logger.debug("WS station send: r=%s station=%s connections=%s", restaurant_id, station_id, len(targets))
        for ws_id in targets:
            await self._safe_send(ws_id, message)

    async def broadcast(
        self,
        restaurant_id: int,
        message: dict
    ):

        targets = list(self._by_restaurant.get(restaurant_id, []))
        logger.debug("WS broadcast: r=%s connections=%s", restaurant_id, len(targets))
        for ws_id in targets:
            await self._safe_send(ws_id, message)

    # =========================
    # SAFE SEND
    # =========================

    async def _safe_send(self, ws_id: int, message: dict):

        conn = self._ws_index.get(ws_id)

        if not conn:
            return

        ws = conn["ws"]

        try:
            logger.info(
                "WS send: ws_id=%s type=%s",
                ws_id,
                message["type"]
            )

            await ws.send_json(message)

        except Exception as e:

            logger.warning("WS send failed: %s", e)

            self.disconnect(ws)


manager = ConnectionManager()