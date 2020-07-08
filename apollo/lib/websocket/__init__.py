import uuid
from typing import Dict

from fastapi import WebSocket
from starlette.types import Message
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosed

from apollo.lib.decorators import notify_websockets
from apollo.lib.exceptions.websocket import SendAfterConnectionClosure
from apollo.lib.schemas.message import BaseMessageSchema
from apollo.lib.singleton import Singleton
from apollo.lib.websocket.interest_type import WebSocketObserverInterestType

SEND_AFTER_CLOSE = (
    "Unexpected ASGI message 'websocket.send', "
    "after sending 'websocket.close'."
)


class WebSocketManager(metaclass=Singleton):
    open_agent_connections: Dict[uuid.UUID, WebSocket] = {}
    open_user_connections: Dict[uuid.UUID, WebSocket] = {}
    open_app_connections: Dict[uuid.UUID, WebSocket] = {}

    @notify_websockets(
        observer_interest_type=WebSocketObserverInterestType.AGENT_LISTING)
    async def connect_agent(self, connection: 'AgentConnection'):
        await connection.accept()
        self.open_agent_connections[connection.id] = connection

    def get_agent_connection(self, agent_id: uuid.UUID):
        return self.open_agent_connections[agent_id]

    @notify_websockets(
        observer_interest_type=WebSocketObserverInterestType.AGENT_LISTING)
    async def close_agent_connection(self, agent_id: uuid.UUID):
        connection = self.get_agent_connection(agent_id)
        await self._close_connection(connection)
        self.open_agent_connections.pop(agent_id)

    async def _close_connection(self, connection: WebSocket):
        try:
            await connection.send_json("Closing connection")
            await connection.close()
        except RuntimeError as e:
            self._raise_if_unexpected_exception(
                error=e,
                message='Cannot call "send" once a close message'
            )
        except ConnectionClosed:
            pass

    async def close_user_connection(self, user_id: uuid.UUID):
        connection = self.get_user_connection(user_id)
        await self._close_connection(connection)
        self.open_user_connections.pop(user_id)

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

    async def message_agent(
        self,
        agent_id: uuid.UUID,
        message: BaseMessageSchema
    ):
        recipient_connection = self.get_agent_connection(agent_id)
        await recipient_connection.send_text(message.json())

    async def message_user(self, user_connection_id, message):
        user_connection = self.get_user_connection(user_connection_id)
        await user_connection.send_text(message)

    @staticmethod
    def _raise_if_unexpected_exception(error, message):
        if message in str(error):
            return

        raise error


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
        if SEND_AFTER_CLOSE in str(error):
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
