import uuid
from typing import Dict

from fastapi import WebSocket

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

    async def connect_user(self, websocket: WebSocket):
        await websocket.accept()
        connection_id = uuid.uuid4()
        self.open_user_connections[connection_id] = websocket
        return connection_id

    def get_user_connection(self, connection_id: uuid.UUID):
        return self.open_user_connections[connection_id]

    async def message_agent(
        self,
        sender_connection_id: uuid.UUID,
        agent_id: uuid.UUID,
        message: str
    ):
        recipient_connection = self.get_agent_connection(agent_id)
        await recipient_connection.send_json({
            'connection_id': str(sender_connection_id),
            'message': message
        })


class ConnectionManager():
    websocket_manager = WebSocketManager()

    def get_connection(self, connection_id):
        raise NotImplementedError

    @staticmethod
    def _raise_if_unexpected_exception(error, message):
        if message in str(error):
            return

        raise error
