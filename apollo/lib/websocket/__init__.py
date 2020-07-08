import uuid
from typing import Dict

from fastapi import WebSocket
from starlette.types import Message
from starlette.websockets import WebSocketDisconnect

from apollo.lib.exceptions.websocket import SendAfterConnectionClosure
from apollo.lib.schemas.message import BaseMessageSchema
from apollo.lib.singleton import Singleton

SEND_AFTER_CLOSE = (
    "Unexpected ASGI message 'websocket.send', "
    "after sending 'websocket.close'."
)
SEND_AFTER_CLOSE_ALTERNATIVE = 'Cannot call "send" once a close message'


class WebSocketManager(metaclass=Singleton):
    open_agent_connections: Dict[uuid.UUID, WebSocket] = {}
    open_user_connections: Dict[uuid.UUID, WebSocket] = {}
    open_app_connections: Dict[uuid.UUID, WebSocket] = {}

    async def connect_app(self, websocket: WebSocket):
        await websocket.accept()
        connection_id = uuid.uuid4()
        self.open_app_connections[connection_id] = websocket
        return connection_id

    def get_app_connection(self, connection_id: uuid.UUID):
        return self.open_app_connections[connection_id]

    async def close_app_connection(self, connection_id: uuid.UUID):
        connection = self.get_app_connection(connection_id)
        await self._close_connection(connection)
        self.open_app_connections.pop(connection_id)


class Connection(WebSocket):
    def __init__(self, websocket: WebSocket, id_: uuid.UUID):
        self.connect(websocket)
        self.id = id_

    async def send(self, message: Message):
        try:
            await super().send(message)
        except RuntimeError as e:
            raise self._convert_runtime_error(e)

    @staticmethod
    def _convert_runtime_error(error: RuntimeError):
        str_error = str(error)
        if (SEND_AFTER_CLOSE in str_error or SEND_AFTER_CLOSE_ALTERNATIVE in
                str_error):
            return SendAfterConnectionClosure()

        return error

    def connect(self, websocket: WebSocket):
        super().__init__(websocket.scope, websocket._receive, websocket._send)
        self.client_state = websocket.client_state
        self.application_state = websocket.application_state

    async def listen(self):
        try:
            while True:
                yield await self._receive_message()
        except WebSocketDisconnect:
            return

    async def _receive_message(self):
        return await self.receive_text()

    async def close(self):
        try:
            super().close()
        except RuntimeError as e:
            raise self._convert_runtime_error(e)


class ConnectionManager:
    websocket_manager = WebSocketManager()
    connections = websocket_manager.open_user_connections

    @classmethod
    async def connect(cls, connection: Connection):
        await connection.accept()
        cls._add_connection(connection)

    @classmethod
    def _add_connection(cls, connection: 'Connection'):
        cls.connections[connection.id] = connection

    @classmethod
    def _remove_connection(cls, connection: 'Connection'):
        cls.connections.pop(connection.id, None)

    @classmethod
    def get_connection(cls, connection_id: uuid.UUID):
        return cls.connections[connection_id]
