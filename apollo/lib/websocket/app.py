import enum
import uuid

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


from apollo.lib.websocket import ConnectionManager


class AppWebSocketConnectionType(enum.Enum):
    AGENT_LISTING = 0


class AppConnectionManager():
    async def connect(
        self, websocket: WebSocket,
        connection_type: AppWebSocketConnectionType
    ):
        connection_id = await self.websocket_manager.connect_app(
            websocket, connection_type)
        await self._listen(connection)
        await self.close_connection(connection_type, connection_id)

    async def _listen(
        self, connection: WebSocket
    ):
        try:
            while True:
                data = await connection.receive_text()
        except WebSocketDisconnect:
            return

    async def close_connection(
        self, connection_type: AppWebSocketConnectionType,
        connection_id: uuid.UUID
    ):
        await self.websocket_managager.close_app_connection(
            connection_type, connection_id)
