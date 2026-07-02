from fastapi import WebSocket
from typing import Dict, Set

class ConnectionManager:
    def __init__(self):
        self.active_rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_key: str):
        await websocket.accept()
        if room_key not in self.active_rooms:
            self.active_rooms[room_key] = set()
        self.active_rooms[room_key].add(websocket)

    def disconnect(self, websocket: WebSocket, room_key: str):
        if room_key in self.active_rooms:
            self.active_rooms[room_key].remove(websocket)
            if not self.active_rooms[room_key]:
                del self.active_rooms[room_key]

    async def broadcast_to_room(self, room_key: str, message: dict):
        if room_key in self.active_rooms:
            for connection in self.active_rooms[room_key]:
                await connection.send_json(message)

manager = ConnectionManager()