"""
In-memory WebSocket connection manager for the chat system.

Each conversation has a "room" — a list of active WebSocket connections.
Messages are broadcast to all connections in a room synchronously within a
single process.

Production note: this design works for a single-instance deployment (e.g. one
Cloud Run revision). For multi-instance horizontal scaling, replace the
in-memory `_rooms` dict with a Redis pub/sub layer — each instance subscribes
to a channel per conversation_id and forwards published messages to its local
WebSocket connections.
"""

from collections import defaultdict
from typing import DefaultDict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        # conversation_id -> list of active WebSocket connections
        self._rooms: DefaultDict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, conversation_id: int) -> None:
        """Accept the WebSocket handshake and register it in the conversation room."""
        await websocket.accept()
        self._rooms[conversation_id].append(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: int) -> None:
        """Remove a connection from its room. Cleans up the room key if empty."""
        room = self._rooms.get(conversation_id, [])
        if websocket in room:
            room.remove(websocket)
        if not room:
            self._rooms.pop(conversation_id, None)

    async def broadcast(self, conversation_id: int, message: dict) -> None:
        """
        Send a message dict as JSON to every connected client in the room.

        Dead connections (send raises) are silently removed so a single
        dropped client does not interrupt the rest of the room.
        """
        dead: list[WebSocket] = []
        for ws in list(self._rooms.get(conversation_id, [])):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, conversation_id)

    def room_size(self, conversation_id: int) -> int:
        """Return the number of active connections in a conversation room."""
        return len(self._rooms.get(conversation_id, []))


# Singleton — import this instance in both REST and WebSocket route modules
# so they share the same in-memory state within a single process.
manager = ConnectionManager()
