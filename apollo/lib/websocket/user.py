import asyncio
import uuid

import click
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.schemas.message import (
    BaseMessageSchema, Command, CommandSchema, ShellIOSchema)
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
            AgentConnection(agent_connection, target_agent_id)
        )
        await shell_connection.listen_and_forward()
        await self.close_connection(user_connection.id)
        return connection_id

    async def _inform_agent_of_new_connection(
        self, connection_id: uuid.UUID, target_agent_id: uuid.UUID
    ):
        await self._message_agent(target_agent_id, CommandSchema(
            connection_id=connection_id,
            command=Command.NEW_CONNECTION
        ))

    async def _listen_and_forward(
        self, connection_id: uuid.UUID, target_agent_id: uuid.UUID,
        connection: WebSocket
    ):
        try:
            while True:
                stdin = await connection.receive_text()
                try:
                    await self._message_agent(
                        target_agent_id,
                        ShellIOSchema(
                            connection_id=connection_id,
                            message=stdin
                        )
                    )
                except KeyError:
                    await self._recover_connection(connection_id,
                                                   target_agent_id)

        except WebSocketDisconnect:
            return

    async def _recover_connection(self, connection_id: uuid.UUID,
                                  target_agent_id: uuid.UUID):
        time_elapsed = 0
        while True:
            if await self._attempt_connection_recovery(
                connection_id, target_agent_id
            ):
                return

            await self._send_connection_lost(connection_id, time_elapsed)
            await asyncio.sleep(1)
            time_elapsed = time_elapsed + 1

    async def _attempt_connection_recovery(self, connection_id: uuid.UUID,
                                           target_agent_id: uuid.UUID):
        try:
            self.websocket_manager.get_agent_connection(target_agent_id)
            await self._message_user(
                connection_id,
                click.style(
                    "\n\r\nConnection recovered\n\r\n",
                    fg='green',
                    bold=True
                )
            )
            await self._inform_agent_of_new_connection(
                connection_id, target_agent_id)
            return True
        except KeyError:
            return False

    async def _send_connection_lost(self, connection_id: uuid.UUID,
                                    time_elapsed: int):
        await self._message_user(
            connection_id,
            click.style(
                "\n\r\nConnection to agent lost. "
                f"Reconnecting.. {time_elapsed}s",
                fg='red',
                bold=True
            )
        )

    async def _message_user(self, connection_id: uuid.UUID, message: str):
        await self.websocket_manager.message_user(connection_id, message)

    async def _message_agent(self, target_agent_id: uuid.UUID,
                             message: BaseMessageSchema):
        await self.websocket_manager.message_agent(target_agent_id, message)

    async def close_connection(self, connection_id: uuid.UUID):
        await self.websocket_manager.close_user_connection(connection_id)

    def get_connection(self, connection_id: uuid.UUID):
        return self.websocket_manager.get_user_connection(connection_id)


class UserConnection(Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, id_=uuid.uuid4(), **kwargs)
