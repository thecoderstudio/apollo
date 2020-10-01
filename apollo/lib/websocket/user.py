import uuid

from fastapi import WebSocket

from apollo.lib.schemas.message import Command
from apollo.lib.websocket.connection import Connection, ConnectionManager
from apollo.lib.websocket.agent import AgentConnectionManager
from apollo.lib.websocket.shell import ShellConnection

TRY_AGAIN_LATER = 1013


class UserConnectionManager(ConnectionManager):
    connections = ConnectionManager.websocket_manager.open_user_connections

    async def connect(self, websocket: WebSocket, target_agent_id: uuid.UUID):
        try:
            agent_connection = self._get_active_agent_connection(
                target_agent_id)
        except KeyError:
            await websocket.close(code=TRY_AGAIN_LATER)
            return

        user_connection = UserConnection(websocket)
        await self._accept_connection(user_connection)

        shell_connection = await ShellConnection.start(
            user_connection,
            agent_connection
        )
        await self._communicate(shell_connection)
        self._remove_connection(user_connection)
        return user_connection

    @staticmethod
    def _get_active_agent_connection(agent_connection_id: uuid.UUID):
        agent_connection = AgentConnectionManager.get_connection(
                agent_connection_id)
        if agent_connection.client_connected:
            return agent_connection

        raise KeyError

    async def _communicate(self, shell_connection: ShellConnection):
        raise NotImplementedError


class UserShellConnectionManager(UserConnectionManager):
    async def _communicate(self, shell_connection: ShellConnection):
        await shell_connection.listen_and_forward()


class UserCommandConnectionManager(UserConnectionManager):
    def __init__(self, *args, command: Command, **kwargs):
        super.__init__(self, *args, **kwargs)
        self.command = command

    async def _communicate(self, shell_connection: ShellConnection):
        await shell_connection.send_command(self.command)


class UserConnection(Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, id_=uuid.uuid4(), **kwargs)
