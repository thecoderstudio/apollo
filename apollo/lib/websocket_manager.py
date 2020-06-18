import uuid

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
from typing import Dict

from apollo.lib.singleton import Singleton


class WebSocketManager(metaclass=Singleton):
    def __init__(self):
        self.connections: Dict[uuid.UUID, WebSocket] = {}
        self.messages: Dict[uuid.UUID, WebSocket] = {}

    async def _keep_connection_open(self, websocket: WebSocket):
        try:
            while True:
                response = await websocket.receive_json()
                requesting_socket = self.messages.pop(response['message_id'])
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

    async def _wait_for_response(self, target_websocket: WebSocket,
                                 message_id: uuid.UUID):
        try:
            while True:
                response = await target_websocket.receive_json()
                try:
                    if response['message_id'] == str(message_id):
                        return response
                except KeyError:
                    continue
        except WebSocketDisconnect:
            return
        except RuntimeError as e:
            self._check_runtime_error(
                error=e,
                message='Cannot call "receive" once a disconnect'
            )

    async def add_and_connect_websocket(self, client_id: uuid.UUID,
                                        websocket: WebSocket):
        self.connections[client_id] = websocket
        await websocket.accept()
        await websocket.send_json("Connection accepted")
        await self._keep_connection_open(websocket)

    async def send_message(
        self, target_websocket_id: uuid.UUID, requesting_socket: WebSocket,
        message: str
    ):
        message_id = uuid.uuid4()
        target_websocket = self.connections[target_websocket_id]
        self.messages[str(message_id)] = requesting_socket
        await self._send_message(
            target_websocket=target_websocket,
            message={
                'message_id': str(message_id),
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
