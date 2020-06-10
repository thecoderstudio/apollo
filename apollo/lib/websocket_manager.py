import asyncio
import uuid

from fastapi import WebSocket
from typing import Dict

from apollo.lib.singleton import Singleton


class WebSocketManager(metaclass=Singleton):
    def __init__(self):
        self.connections: Dict[uuid.UUID, WebSocket] = {}

    async def add_and_connect_websocket(self, websocket: WebSocket):
        self.connections[uuid.uuid4()] = websocket
        await websocket.accept()
        await websocket.send_json("Connection accepted")
        await websocket.receive()

    async def send_message(self, websocket_id: uuid.UUID, message: str):
        websocket = self.connections[websocket_id]
        await self.connections[websocket_id].send_text(message)

    async def close_and_remove_connection(self, websocket_id):
        websocket = self.connections.pop(websocket_id)
        await self.connections[websocket_id].send_json("Closing connection.")
        await websocket.close()
