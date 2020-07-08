import uuid

from fastapi import WebSocket

from apollo.lib.schemas.message import BaseMessageSchema, ShellIOSchema
from apollo.lib.websocket import ConnectionManager, Connection
from apollo.lib.websocket.user import UserConnectionManager


class AgentConnectionManager(ConnectionManager):
    async def connect(self, agent_id: uuid.UUID, websocket: WebSocket):
        try:
            connection = self.get_connection(agent_id)
            connection.connect(websocket)
        except KeyError:
            connection = AgentConnection(websocket, agent_id)

        await self.websocket_manager.connect_agent(connection)
        await connection.listen_and_forward()

    async def close_connection(self, connection_id: uuid.UUID):
        await self.websocket_manager.close_agent_connection(connection_id)

    async def close_all_connections(self):
        for agent_id in list(self.websocket_manager.open_agent_connections):
            await self.close_connection(agent_id)


class AgentConnection(Connection):
    async def message(self, message: BaseMessageSchema):
        await self.send_text(message.json())

    async def listen_and_forward(self):
        async for response in self.listen():
            await self.message_over_user_connection(ShellIOSchema(**response))

    async def _receive_message(self):
        return await self.receive_json()

    async def message_over_user_connection(self, message: ShellIOSchema):
        user_connection = self._get_user_connection(message.connection_id)
        await user_connection.send_text(message.message)

    def _get_user_connection(self, connection_id: uuid.UUID):
        return UserConnectionManager.get_connection(connection_id)
