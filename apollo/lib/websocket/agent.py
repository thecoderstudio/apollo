import uuid

from fastapi import WebSocket

from apollo.lib.decorators import notify_websockets
from apollo.lib.exceptions.websocket import SendAfterConnectionClosure
from apollo.lib.schemas.message import BaseMessageSchema, ShellIOSchema
from apollo.lib.websocket.connection import ConnectionManager, Connection
from apollo.lib.websocket.interest_type import WebSocketObserverInterestType


class AgentConnectionManager(ConnectionManager):
    connections = ConnectionManager.websocket_manager.agent_connections

    async def connect(self, agent_id: uuid.UUID, websocket: WebSocket):
        try:
            connection = self.get_connection(agent_id)
            connection.connect(websocket)
        except KeyError:
            connection = AgentConnection(websocket, agent_id)

        await self._accept_connection(connection)
        await connection.listen_and_forward()

    async def close_connection(self, connection_id: uuid.UUID):
        connection = self.get_connection(connection_id)

        try:
            await connection.close()
        except SendAfterConnectionClosure:
            pass

    async def close_all_connections(self):
        for agent_id in list(self.connections):
            await self.close_connection(agent_id)


class AgentConnection(Connection):
    async def message(self, message: BaseMessageSchema):
        await self.send_text(message.json())

    async def listen_and_forward(self):
        async for response in self.listen():
            await self._message_over_user_connection(ShellIOSchema(**response))

    async def _receive_message(self):
        return await self.receive_json()

    async def _message_over_user_connection(self, message: ShellIOSchema):
        user_connection = self._get_user_connection(message.connection_id)
        await user_connection.send_text(message.message)

    @staticmethod
    def _get_user_connection(connection_id: uuid.UUID):
        from apollo.lib.websocket.user import UserConnectionManager
        return UserConnectionManager.get_connection(connection_id)

    @notify_websockets(
        observer_interest_type=WebSocketObserverInterestType.AGENT_LISTING)
    async def accept(self):
        await super().accept()

    @notify_websockets(
        observer_interest_type=WebSocketObserverInterestType.AGENT_LISTING)
    async def close(self):
        await super().close()
