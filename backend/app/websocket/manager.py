from fastapi import WebSocket
from collections import defaultdict
from app.models.user import UserRole


class ConnectionManager:

    def __init__(self):
        # restaurant_id -> list of connections
        self.connections = defaultdict(list)
        self._ws_index = {}

    async def connect(self, websocket, user, station_id=None):
        await websocket.accept()
        conn = {"ws": websocket, "user": user, "station_id": station_id}
        self.connections[user.restaurant_id].append(conn)
        self._ws_index[id(websocket)] = user.restaurant_id
        print(f"WS connected r={user.restaurant_id} role={user.role}")


    def disconnect(self, websocket):
        restaurant_id = self._ws_index.pop(id(websocket), None)
        if restaurant_id:
            self.connections[restaurant_id] = [
                c for c in self.connections[restaurant_id]
                if c["ws"] != websocket
            ]
        print("WS disconnected")

    # =========================
    # ENVÍOS
    # =========================

    async def send_to_role(self, restaurant_id: int, role: UserRole, message: dict):

        for c in self.connections[restaurant_id]:
            if c["user"].role == role:
                await self._safe_send(c["ws"], message)

    async def send_to_station(self, restaurant_id: int, station_id: int, message: dict):

        for c in self.connections[restaurant_id]:
            if c["station_id"] == station_id:
                await self._safe_send(c["ws"], message)

    async def broadcast(self, restaurant_id: int, message: dict):

        for c in self.connections[restaurant_id]:
            await self._safe_send(c["ws"], message)

    async def _safe_send(self, ws: WebSocket, message: dict):
        try:
            await ws.send_json(message)
        except Exception as e:
            print("WS send failed", e)


manager = ConnectionManager()