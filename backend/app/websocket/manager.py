from fastapi import WebSocket
from collections import defaultdict


class ConnectionManager:

    def __init__(self):

        # restaurant -> station -> kitchen connections
        self.connections = defaultdict(lambda: defaultdict(list))

        # restaurant -> waiter connections
        self.waiters = defaultdict(list)


    # =========================
    # KITCHEN
    # =========================

    async def connect(self, websocket: WebSocket, restaurant_id: int, station_id: int):

        await websocket.accept()

        self.connections[restaurant_id][station_id].append(websocket)

        print(f"WS kitchen connected r={restaurant_id} s={station_id}")


    def disconnect(self, websocket: WebSocket, restaurant_id: int, station_id: int):

        if websocket in self.connections[restaurant_id][station_id]:
            self.connections[restaurant_id][station_id].remove(websocket)

        print(f"WS kitchen disconnected r={restaurant_id} s={station_id}")


    async def send_to_station(self, restaurant_id: int, station_id: int, message: dict):

        dead = []

        for connection in self.connections[restaurant_id][station_id]:
            try:
                await connection.send_json(message)
            except:
                dead.append(connection)

        for conn in dead:
            self.connections[restaurant_id][station_id].remove(conn)

        print(
            f"Kitchen broadcast to {len(self.connections[restaurant_id][station_id])} clients"
        )


    # =========================
    # WAITERS
    # =========================

    async def connect_waiter(self, websocket: WebSocket, restaurant_id: int):

        await websocket.accept()

        self.waiters[restaurant_id].append(websocket)

        print(f"WS waiter connected r={restaurant_id}")


    def disconnect_waiter(self, websocket: WebSocket, restaurant_id: int):

        if websocket in self.waiters[restaurant_id]:
            self.waiters[restaurant_id].remove(websocket)

        print(f"WS waiter disconnected r={restaurant_id}")


    async def send_to_waiters(self, restaurant_id: int, message: dict):

        dead = []

        for connection in self.waiters[restaurant_id]:
            try:
                await connection.send_json(message)
            except:
                dead.append(connection)

        for conn in dead:
            self.waiters[restaurant_id].remove(conn)

        print(
            f"Waiter broadcast to {len(self.waiters[restaurant_id])} clients"
        )


manager = ConnectionManager()