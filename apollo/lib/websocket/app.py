from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.websocket import ConnectionManager
from apollo.lib.websocket.interest_type import WebSocketObserverInterestType


class AppConnectionManager(ConnectionManager):
    @staticmethod
    async def _listen(connection: WebSocket):
        try:
            while True:
                await connection.receive_text()
        except WebSocketDisconnect:
            return

    async def connect_and_send(
        self, websocket: WebSocket,
        connection_type: WebSocketObserverInterestType
    ):
        connection_id = await self.websocket_manager.connect_app(
            websocket, connection_type)
        await websocket.send_json(connection_type.run_corresponding_function())
        await self.websocket_manager.close_app_connection(
            connection_type, connection_id)

    async def send_message_to_connections(
        self, connection_type: WebSocketObserverInterestType
    ):
        for websocket in (
            self.websocket_manager.open_app_connections.get(
                connection_type, {}).values()
        ):
            await websocket.send_json(
                connection_type.run_corresponding_function())
