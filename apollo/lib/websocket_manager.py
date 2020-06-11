import asyncio
import uuid

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
from typing import Dict

from apollo.lib.singleton import Singleton

class WebSocketManager(metaclass=Singleton):
    def __init__(self):
        self.connections: Dict[uuid.UUID, WebSocket] = {}

    async def add_and_connect_websocket(self, websocket: WebSocket):
        self.connections[uuid.uuid4()] = websocket
        await websocket.accept()
        await websocket.send_json("Connection accepted")
        try: 
            await websocket.receive_json() 
        except WebSocketDisconnect:
            return


    async def send_message(self, websocket_id: uuid.UUID, message: str):
        websocket = self.connections[websocket_id]
        await self.connections[websocket_id].send_json(message)

    async def close_and_remove_connection(self, websocket_id):
        websocket = self.connections.pop(websocket_id)
        try:
            await self.connections[websocket_id].send_json("Closing connection")
            await websocket.close()
        except RuntimeError:
            # Connection already closed
            return

    async def close_and_remove_all_connections(self):
        for connection in self.connections.values():
            await connection.close()
        self.connections = {}
