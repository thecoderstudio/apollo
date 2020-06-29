import uuid
from typing import Dict

from fastapi import WebSocket
from websockets.exceptions import ConnectionClosed

from apollo.lib.schemas.message import BaseMessageSchema
from apollo.lib.singleton import Singleton


class WebSocketManager(metaclass=Singleton):
    def __init__(self):
        self.open_agent_connections: Dict[uuid.UUID, WebSocket] = {}
        self.open_user_connections: Dict[uuid.UUID, WebSocket] = {}

    async def connect_agent(self, agent_id: uuid.UUID, websocket: WebSocket):
        await websocket.accept()
        self.open_agent_connections[agent_id] = websocket

    def get_agent_connection(self, agent_id: uuid.UUID):
        return self.open_agent_connections[agent_id]

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

    async def connect_user(self, websocket: WebSocket):
        await websocket.accept()
        connection_id = uuid.uuid4()
        self.open_user_connections[connection_id] = websocket
        return connection_id

    def get_user_connection(self, connection_id: uuid.UUID):
        return self.open_user_connections[connection_id]

    async def message_agent(
        self,
        agent_id: uuid.UUID,
        message: BaseMessageSchema
    ):
        recipient_connection = self.get_agent_connection(agent_id)
        print(message.json())
        await recipient_connection.send_text(message.json())

    async def message_user(self, user_connection_id, message):
        user_connection = self.get_user_connection(user_connection_id)
        await user_connection.send_text(message)

    @staticmethod
    def _raise_if_unexpected_exception(error, message):
        if message in str(error):
            return

        raise error


class ConnectionManager():
    websocket_manager = WebSocketManager()

    def get_connection(self, connection_id: uuid.UUID):
        raise NotImplementedError

    async def close_connection(self, connection_id: uuid.UUID):
        raise NotImplementedError
