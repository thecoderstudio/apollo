import uuid

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.websocket import ConnectionManager


class UserConnectionManager(ConnectionManager):
    async def connect(self, websocket: WebSocket, target_agent_id: uuid.UUID):
        connection_id = await self.websocket_manager.connect_user(websocket)
        await self._listen_and_forward(connection_id, target_agent_id,
                                       websocket)

    async def _listen_and_forward(
        self, connection_id: uuid.UUID, target_agent_id: uuid.UUID,
        connection: WebSocket
    ):
        try:
            while True:
                command = await connection.receive_text()
                await self.websocket_manager.message_agent(
                    connection_id, target_agent_id, command)
        except WebSocketDisconnect:
            return

    def get_connection(self, connection_id: uuid.UUID):
        return self.websocket_manager.get_user_connection(connection_id)
