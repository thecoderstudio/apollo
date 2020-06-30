import asyncio
import uuid

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.schemas.message import (
    BaseMessageSchema, Command, CommandSchema, ShellMessageSchema)
from apollo.lib.websocket import ConnectionManager

TRY_AGAIN_LATER = 1013


class UserConnectionManager(ConnectionManager):
    async def connect(self, websocket: WebSocket, target_agent_id: uuid.UUID):
        if not await self._verify_agent_connection(websocket, target_agent_id):
            return

        connection_id = await self.websocket_manager.connect_user(websocket)
        await self._inform_agent_of_new_connection(
            connection_id, target_agent_id, websocket)
        await self._listen_and_forward(connection_id, target_agent_id,
                                       websocket)
        await self.close_connection(connection_id)
        return connection_id

    async def _verify_agent_connection(self, websocket: WebSocket,
                                       target_agent_id: uuid.UUID):
        try:
            self.websocket_manager.get_agent_connection(target_agent_id)
        except KeyError:
            await websocket.close(code=TRY_AGAIN_LATER)
            return False

        return True

    async def _inform_agent_of_new_connection(
        self, connection_id: uuid.UUID, target_agent_id: uuid.UUID,
        connection: WebSocket
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
                await self._message_agent(
                    target_agent_id,
                    ShellMessageSchema(
                        connection_id=connection_id,
                        message=stdin
                    )
                )
        except WebSocketDisconnect:
            return

    async def _message_agent(self, target_agent_id: uuid.UUID,
                             message: BaseMessageSchema):
        asyncio.create_task(
            self.websocket_manager.message_agent(
                target_agent_id, message)
        )

    async def close_connection(self, connection_id: uuid.UUID):
        await self.websocket_manager.close_user_connection(connection_id)

    def get_connection(self, connection_id: uuid.UUID):
        return self.websocket_manager.get_user_connection(connection_id)
