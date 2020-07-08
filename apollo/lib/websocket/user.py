import uuid

from fastapi import WebSocket

from apollo.lib.websocket import Connection, ConnectionManager
from apollo.lib.websocket.agent import AgentConnection
from apollo.lib.websocket.shell import ShellConnection

TRY_AGAIN_LATER = 1013


class UserConnectionManager(ConnectionManager):
    async def connect(self, websocket: WebSocket, target_agent_id: uuid.UUID):
        try:
            agent_connection = self.websocket_manager.get_agent_connection(
                target_agent_id)
        except KeyError:
            await websocket.close(code=TRY_AGAIN_LATER)
            return

        user_connection = UserConnection(websocket)
        connection_id = await self.websocket_manager.connect_user(
            user_connection)

        shell_connection = await ShellConnection.start(
            user_connection,
            agent_connection
        )
        await shell_connection.listen_and_forward()
        await self.close_connection(user_connection.id)
        return connection_id

    async def close_connection(self, connection_id: uuid.UUID):
        await self.websocket_manager.close_user_connection(connection_id)

    def get_connection(self, connection_id: uuid.UUID):
        return self.websocket_manager.get_user_connection(connection_id)


class UserConnection(Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, id_=uuid.uuid4(), **kwargs)
