import uuid

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
from typing import Dict

from apollo.lib.singleton import Singleton


class WebSocketManager(metaclass=Singleton):
    def __init__(self):
        self.connections: Dict[uuid.UUID, WebSocket] = {}

    @staticmethod
    async def _keep_connection_open(websocket: WebSocket):
        try:
            await websocket.receive_json()
        except WebSocketDisconnect:
            return

    async def add_and_connect_websocket(self, id: uuid.UUID,
                                        websocket: WebSocket):
        self.connections[id] = websocket
        await websocket.accept()
        await websocket.send_json("Connection accepted")
        try:
            return await websocket.receive_json()
        except WebSocketDisconnect:
            print("**" * 10)
            return

    async def send_message(self, websocket_id: uuid.UUID, message: str):
        message_id = uuid.uuid4()
        await self.connections[websocket_id].send_json({
            'message_id': str(message_id),
            'message': message
        })
        return message_id

    async def wait_for_response(self, websocket_id: uuid.UUID,
                                message_id: uuid.UUID):
        while True:
            try:
                response = await self.connections[websocket_id].receive_json()
                if response['message_id'] == str(message_id):
                    return response
            except KeyError:
                continue
            except WebSocketDisconnect:
                return

    async def close_and_remove_connection(self, websocket_id):
        websocket = self.connections.pop(websocket_id)
        try:
            print("--")
            print(websocket_id)
            await websocket.send_json("Closing connection")
            await websocket.close()
        except RuntimeError:
            # Connection already closed
            return

    async def close_and_remove_all_connections(self):
        for id_ in list(self.connections):
            await self.close_and_remove_connection(id_)
        self.connections = {}
