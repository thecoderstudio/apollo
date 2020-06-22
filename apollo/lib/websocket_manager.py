import uuid
from typing import Dict

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.singleton import Singleton


class WebSocketManager(metaclass=Singleton):
    def __init__(self):
        self.connections: Dict[uuid.UUID, WebSocket] = {}

    @staticmethod
    async def _keep_connection_open(websocket: WebSocket):
        try:
            while True:
                await websocket.receive_json()
        except WebSocketDisconnect:
            return

    @staticmethod
    async def _send_message(target_websocket, message):
        await target_websocket.send_json(message)

    @staticmethod
    def _raise_if_unexpected_exception(error, message):
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
            self._raise_if_unexpected_exception(
                error=e,
                message='Cannot call "receive" once a disconnect'
            )

    async def add_and_connect_websocket(self, client_id: uuid.UUID,
                                        websocket: WebSocket):
        self.connections[client_id] = websocket
        await websocket.accept()
        await websocket.send_json("Connection accepted")
        await self._keep_connection_open(websocket)

    async def send_message_and_wait_for_response(
        self, target_websocket_id: uuid.UUID,
        message: str
    ):

        message_id = uuid.uuid4()
        target_websocket = self.connections[target_websocket_id]
        await self._send_message(
            target_websocket=target_websocket,
            message={
                'message_id': str(message_id),
                'message': message
            })
        return await self._wait_for_response(
            target_websocket=target_websocket,
            message_id=message_id
        )

    async def close_and_remove_connection(self, websocket_id):
        websocket = self.connections.pop(websocket_id)
        try:
            await websocket.send_json({
                'session_id': str(uuid.uuid4()),
                'message': "close and remove"
            })
            await websocket.close()
        except RuntimeError as e:
            self._raise_if_unexpected_exception(
                error=e,
                message='Cannot call "send" once a close message'
            )

    async def close_and_remove_all_connections(self):
        for id_ in list(self.connections):
            await self.close_and_remove_connection(id_)
