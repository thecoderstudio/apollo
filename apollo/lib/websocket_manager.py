import asyncio
import uuid

from fastapi import WebSocket
# from starlette.websockets import WebSocketState
from typing import Dict

from apollo.lib.singleton import Singleton


class WebSocketManager:
    __metaclass__ = Singleton

    def __init__(self):
        self.connections: Dict[uuid.UUID, WebSocket] = {}

    async def add_and_connect_websocket(self, websocket: WebSocket):
        id = uuid.uuid4()
        print(id)
        self.connections[id] = websocket
        await websocket.accept()
        await websocket.receive()
        try:
            while True:
                await asyncio.sleep(1)
        finally:
            await websocket.close()

    async def send_message(self, websocket_id: uuid.UUID, message: str):
        websocket = self.connection[websocket_id]
        await self.connection[websocket_id].send_text(message)

    async def close_and_remove_connection(self, websocket_id):
        websocket = self.connection.pop(websocket_id)
        await websocket.close()
