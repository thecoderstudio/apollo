import uuid

from fastapi import WebSocket

from apollo.lib.websocket import Connection, ConnectionManager
from apollo.lib.websocket.agent import AgentConnectionManager
from apollo.lib.websocket.shell import ShellConnection

TRY_AGAIN_LATER = 1013


class UserConnectionManager(ConnectionManager):
    async def connect(self, websocket: WebSocket, target_agent_id: uuid.UUID):
        try:
            agent_connection = AgentConnectionManager.get_connection(
                target_agent_id)
        except KeyError:
            await websocket.close(code=TRY_AGAIN_LATER)
            return

        user_connection = UserConnection(websocket)
        await super().connect(user_connection)

        shell_connection = await ShellConnection.start(
            user_connection,
            agent_connection
        )
        await shell_connection.listen_and_forward()
        self._remove_connection(user_connection.id)
        return user_connection


class UserConnection(Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, id_=uuid.uuid4(), **kwargs)
