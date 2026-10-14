"""
backend/core/ws_manager.py
---------------------------
Minimal WebSocket connection manager for the admin dashboard's Live Feed.
Keeps a set of connected clients and broadcasts JSON events to all of them.
"""

from fastapi import WebSocket
from typing import List, Dict, Any
from backend.core.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Dashboard client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Dashboard client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        stale = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                stale.append(connection)
        for conn in stale:
            self.disconnect(conn)


# Single shared instance imported by dashboard.py and chat.py
ws_manager = ConnectionManager()
