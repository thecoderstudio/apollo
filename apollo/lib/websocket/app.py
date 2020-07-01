import enum
import json

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.decorators import with_db_session


class WebSocketObserverInterestTypes(enum.Enum):
    @staticmethod
    @with_db_session
    def _list_all_agents(session):
        from apollo.models.agent import list_all_agents
        from apollo.lib.schemas.agent import BaseAgentSchema

        return [json.loads(BaseAgentSchema.from_orm(agent).json()) for
                agent in list_all_agents(session)]

    AGENT_LISTING = _list_all_agents


class AppConnectionManager:
    def __init__(self):
        from apollo.lib.websocket import WebSocketManager
        self.websocket_manager = WebSocketManager()

    @staticmethod
    async def _listen(connection: WebSocket):
        try:
            while True:
                await connection.receive_text()
        except WebSocketDisconnect:
            return

    async def connect_and_send(
        self, websocket: WebSocket,
        connection_type: WebSocketObserverInterestTypes
    ):
        connection_id = await self.websocket_manager.connect_app(
            websocket, connection_type)
        await websocket.send_json(connection_type())
        await self._listen(websocket)
        await self.websocket_manager.close_app_connection(
            connection_type, connection_id)(connection_type, connection_id)

    async def send_message_to_connections(
            self, connection_type: WebSocketObserverInterestTypes):
        for websocket in (
            self.websocket_manager.open_app_connections.get(
                connection_type, {}).values()
        ):
            await websocket.send_json(
                connection_type()
            )
