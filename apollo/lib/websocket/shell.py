import asyncio

import click
from starlette.websockets import WebSocketDisconnect, WebSocketState

from apollo.lib.schemas.message import Command, CommandSchema, ShellIOSchema


class ShellConnection:
    @classmethod
    async def start(cls, origin: 'UserConnection', target: 'AgentConnection'):
        self = ShellConnection()
        self.origin = origin
        self.target = target
        await self.alert_target_of_new_connection()
        return self

    async def alert_target_of_new_connection(self):
        await self.target.message(CommandSchema(
            connection_id=self.origin.id,
            command=Command.NEW_CONNECTION
        ))

    async def listen_and_forward(self):
        try:
            while True:
                stdin = await self.origin.receive_text()
                await self._message_target(stdin)
        except WebSocketDisconnect:
            return

    async def _message_target(self, message):
        try:
            await self.target.message(
                ShellIOSchema(
                    connection_id=self.origin.id,
                    message=message
                )
            )
        except KeyError:
            await self._recover()

    async def _recover(self):
        time_elapsed = 0
        while True:
            if await self._attempt_recovery():
                return

            await self._alert_origin_of_lost_connection(time_elapsed)
            await asyncio.sleep(1)
            time_elapsed = time_elapsed + 1

    async def _attempt_recovery(self):
        if self.target.client_state is not WebSocketState.CONNECTED:
            return False

        await self.origin.message(click.style(
            "\n\r\nConnection recovered\n\r\n",
            fg='green',
            bold=True
        ))
        await self._alert_target_of_new_connection()
        return True

    async def _alert_origin_of_lost_connection(self, time_elapsed):
        await self.origin.message(click.style(
            f"\n\r\nConnection to agent lost. Reconnecting.. {time_elapsed}s",
            fg='red',
            bold=True
        ))
