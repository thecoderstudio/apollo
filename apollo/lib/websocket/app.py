from typing import Dict
import enum
import uuid

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.decorators import with_db_session


class WebSocketInterest(enum.Enum):
    AGENT_LISTING = 0


class AppConnectionManager():

    def __init__(self, *args, **kwargs):
        from apollo.lib.websocket import WebSocketManager
        self.websocket_manager = WebSocketManager()
        self.websocket_interest_functions: Dict[WebSocketInterest] = {
            WebSocketInterest.AGENT_LISTING: self._list_all_agents
        }

    @with_db_session
    def _list_all_agents(session):
        from apollo.models.agent import list_all_agents
        pass
        # from apollo.lib.schemas.agent import BaseAgentSchema
        # return BaseAgentSchema.from_orm(list_all_agents(session))

    async def connect(
        self, websocket: WebSocket,
        connection_type: WebSocketInterest
    ):
        connection_id = await self.websocket_manager.connect_app(
            websocket, connection_type)
        await self._listen(websocket)
        await self.close_connection(connection_type, connection_id)

    async def send_message_to_connections(self,
                                          connection_type: WebSocketInterest):
        for connection in (
            self.websocket_manager.open_app_connections[connection_type]
        ):
            await self.websocket_manager.connection.send_json(
                self.websocket_interest_functions[connection_type]()
            )

    @staticmethod
    async def _listen(connection: WebSocket):
        try:
            while True:
                data = await connection.receive_text()
        except WebSocketDisconnect:
            return

    async def close_connection(
        self, connection_type: WebSocketInterest,
        connection_id: uuid.UUID
    ):
        await self.websocket_managager.close_app_connection(
            connection_type, connection_id)
