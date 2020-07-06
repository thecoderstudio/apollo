import uuid
from typing import Dict, List

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.websocket import ConnectionManager
from apollo.lib.websocket.interest_type import WebSocketObserverInterestType


class AppConnectionManager(ConnectionManager):
    interested_connections: Dict[WebSocketObserverInterestType,
                                 List[uuid.UUID]] = {}

    @staticmethod
    async def _listen(connection: WebSocket):
        try:
            while True:
                await connection.receive_text()
        except WebSocketDisconnect:
            return

    def _add_interested_connection(
        self,
        observer_interest_type: WebSocketObserverInterestType,
        connection_id: uuid.UUID
    ):
        connections = self.interested_connections.get(observer_interest_type,
                                                      [])
        connections.append(connection_id)
        self.interested_connections[observer_interest_type] = connections

    async def _close_and_remove_connection(self, connection_id: uuid.UUID):
        await self.close_connection(connection_id)
        for connection_list in self.interested_connections.values():
            try:
                connection_list.remove(connection_id)
            except ValueError:
                pass

    async def connect_and_send(
        self, websocket: WebSocket,
        observer_interest_type: WebSocketObserverInterestType
    ):
        connection_id = await self.websocket_manager.connect_app(
            websocket)
        self._add_interested_connection(observer_interest_type, connection_id)
        await websocket.send_json(
            observer_interest_type.run_corresponding_function())
        await self._listen(websocket)
        await self._close_and_remove_connection(connection_id)

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
        return self.websocket_manager.get_app_connection(connection_id)

    async def close_connection(self, connection_id: uuid.UUID):
        await self.websocket_manager.close_app_connection(connection_id)

