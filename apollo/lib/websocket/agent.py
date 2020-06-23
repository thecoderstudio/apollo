import uuid

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.websocket import ConnectionManager


class AgentConnectionManager(ConnectionManager):
    async def connect(self, agent_id: uuid.UUID, websocket: WebSocket):
        await self.websocket_manager.connect_agent(agent_id, websocket)
        await websocket.send_json("Connection accepted")
        await self._listen_and_forward(websocket)

    async def _listen_and_forward(self, connection: WebSocket):
        try:
            while True:
                response = await connection.receive_json()
                recipient_socket = self.websocket_manager.get_user_connection(
                    uuid.UUID(response['connection_id'])
                )
                await recipient_socket.send_text(response['message'])
        except WebSocketDisconnect:
            return

    async def close_connection(self, agent_id: uuid.UUID):
        connection = self.get_connection(agent_id)
        try:
            await connection.send_json("Closing connection")
            await connection.close()
        except RuntimeError as e:
            self._raise_if_unexpected_exception(
                error=e,
                message='Cannot call "send" once a close message'
            )

    async def close_all_connections(self):
        for agent_id in list(self.websocket.open_agent_connections):
            await self.close_connection(agent_id)

    def get_connection(self, connection_id: uuid.UUID):
        return self.websocket_manager.get_agent_connection(connection_id)
