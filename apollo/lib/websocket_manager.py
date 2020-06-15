import uuid

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
from typing import Dict

from apollo.lib.singleton import Singleton


class WebSocketManager(metaclass=Singleton):
    def __init__(self):
        self.connections: Dict[uuid.UUID, WebSocket] = {}

    async def add_and_connect_websocket(self, id: uuid.UUID, websocket: WebSocket):
        self.connections[id] = websocket
        print(websocket)
        print(dir(websocket))
        print(websocket.headers)
        print(websocket.client)
        await websocket.accept()
        await websocket.send_json("Connection accepted")
        try:
            return await websocket.receive_json()
        except WebSocketDisconnect:
            return

    async def send_message(self, websocket_id: uuid.UUID, message: str):
        await self.connections[websocket_id].send_json(message)

    async def close_and_remove_connection(self, websocket_id):
        websocket = self.connections.pop(websocket_id)
        try:
            await websocket.send_json("Closing connection")
            await websocket.close()
        except RuntimeError:
            # Connection already closed
            return

    async def close_and_remove_all_connections(self):
        for id_ in list(self.connections):
            await self.close_and_remove_connection(id_)
        self.connections = {}
