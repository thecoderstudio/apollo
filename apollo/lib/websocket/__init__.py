import uuid

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
from typing import Dict

from apollo.lib.singleton import Singleton


class WebSocketManager(metaclass=Singleton):
    def __init__(self):
        self.connections: Dict[uuid.UUID, WebSocket] = {}
        self.sessions: Dict[uuid.UUID, WebSocket] = {}

    async def _keep_connection_open(self, websocket: WebSocket):
        try:
            while True:
                response = await websocket.receive_json()
                requesting_socket = self.sessions[
                    uuid.UUID(response['session_id'])
                ]
                await requesting_socket.send_text(response['message'])
        except WebSocketDisconnect:
            return

    @staticmethod
    async def _send_message(target_websocket, message):
        await target_websocket.send_json(message)

    @staticmethod
    def _check_runtime_error(error, message):
        if message in str(error):
            return

        raise error

    async def add_and_connect_websocket(self, client_id: uuid.UUID,
                                        websocket: WebSocket):
        self.connections[client_id] = websocket
        await websocket.accept()
        await websocket.send_json("Connection accepted")
        await self._keep_connection_open(websocket)

    async def send_message(
        self, target_websocket_id: uuid.UUID, session_id: uuid.UUID,
        message: str
    ):
        target_websocket = self.connections[target_websocket_id]
        await self._send_message(
            target_websocket=target_websocket,
            message={
                'session_id': str(session_id),
                'message': message
            })

    async def close_and_remove_connection(self, websocket_id):
        websocket = self.connections.pop(websocket_id)
        try:
            await websocket.send_json("Closing connection")
            await websocket.close()
        except RuntimeError as e:
            self._check_runtime_error(
                error=e,
                message='Cannot call "send" once a close message'
            )

    async def close_and_remove_all_connections(self):
        for id_ in list(self.connections):
            await self.close_and_remove_connection(id_)
        self.connections = {}
