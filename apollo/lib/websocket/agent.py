import uuid

from fastapi import WebSocket

from apollo.lib.decorators import notify_websockets
from apollo.lib.schemas.message import BaseMessageSchema
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
        await connection.close()

    async def close_all_connections(self):
        for agent_id in list(self.connections):
            await self.close_connection(agent_id)


class AgentConnection(Connection):
    async def message(self, message: BaseMessageSchema):
        await self.send_text(message.json())

    async def listen_and_forward(self):
        async for response in self.listen():
            await self._process_response(response)

    async def _process_response(self, response: dict):
        from apollo.lib.websocket.user import UserConnectionManager
        await UserConnectionManager.process_agent_response(response)

    async def _receive_message(self):
        return await self.receive_json()

    @notify_websockets(
        observer_interest_type=WebSocketObserverInterestType.AGENT_LISTING)
    async def accept(self):
        await super().accept()

    @notify_websockets(
        observer_interest_type=WebSocketObserverInterestType.AGENT_LISTING)
    async def close(self):
        await super().close()
