import enum
import uuid

from fastapi import WebSocket
from starlette import WebSOcketDisconnect


from apollo.lib.websocket import ConnectionManager


class AppSocketConnectionType(enum.Enum):
    AGENT_LISTING = 0


class AppConnectionManager(connectionManager):
    async def connect(self, websocket: WebSocket,
                      connection_type: WebSocketConnectionType):
        connection_id = await self.websocket_manager.connect_app(
            websocket, connection_type)

    async def close_connection(self, connection_id: uuid.UUID):
        # await self.websocket_managager.close_web_connection
        pass

    def get_connection(self, connection_id: uuid.UUID):
        pass
