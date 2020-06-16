import asyncio
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
            while True:
                await websocket.receive_json()
        except WebSocketDisconnect:
            return

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
        loop = asyncio.get_event_loop()
        loop.create_task(
            self._wait_for_response(
                target_websocket=target_websocket,
                message_id=message_id
            )
        )
        await self._send_message(
            target_websocket=target_websocket,
            message={
                'message_id': str(message_id),
                'message': message
            })

    @staticmethod
    async def _send_message(target_websocket, message):
        await target_websocket.send_json(message)

    async def _wait_for_response(self, target_websocket: WebSocket,
                                 message_id: uuid.UUID):
        while True:
            try:
                response = await target_websocket.receive_json()
                if response['message_id'] == str(message_id):
                    # message received.
                    pass
            except KeyError:
                continue
            except (WebSocketDisconnect, RuntimeError):
                return

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
