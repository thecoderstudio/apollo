import uuid

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
        observer_interest_type: WebSocketObserverInterestType
    ):
        connection_id = await self.websocket_manager.connect_app(
            websocket, observer_interest_type)
        await websocket.send_json(
            observer_interest_type.run_corresponding_function())
        await self.websocket_manager.close_app_connection(
            observer_interest_type, connection_id)

    async def send_message_to_connections(
        self, observer_interest_type: WebSocketObserverInterestType
    ):
        for websocket in (
            self.websocket_manager.open_app_connections.get(
                observer_interest_type, {}).values()
        ):
            await websocket.send_json(
                observer_interest_type.run_corresponding_function())

    def get_connection(self, connection_id: uuid.UUID):
        raise NotImplementedError

    async def close_connection(self, connection_id: uuid.UUID):
        raise NotImplementedError
