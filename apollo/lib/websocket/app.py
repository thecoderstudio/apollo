import json
import uuid
from typing import Dict, Set

from fastapi import WebSocket
from pydantic.json import pydantic_encoder
from starlette.websockets import WebSocketDisconnect

from apollo.lib.singleton import Singleton
from apollo.lib.websocket import ConnectionManager
from apollo.lib.websocket.interest_type import WebSocketObserverInterestType


class AppConnectionManager(ConnectionManager, metaclass=Singleton):
    interested_connections: Dict[WebSocketObserverInterestType,
                                 Set[uuid.UUID]] = {}

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
                                                      set())
        connections.add(connection_id)
        self.interested_connections[observer_interest_type] = connections

    async def _close_and_remove_connection(self, connection_id: uuid.UUID):
        await self.close_connection(connection_id)
        for connection_set in self.interested_connections.values():
            connection_set.discard(connection_id)

    async def _send_message(
        self, websocket_id: uuid.UUID,
        observer_interest_type: WebSocketObserverInterestType
    ):
        await self.get_connection(websocket_id).send_text(json.dumps(
            observer_interest_type.run_corresponding_function(),
            default=pydantic_encoder))

    async def connect_and_send(
        self, websocket: WebSocket,
        observer_interest_type: WebSocketObserverInterestType
    ):
        connection_id = await self.websocket_manager.connect_app(websocket)
        self._add_interested_connection(observer_interest_type, connection_id)
        await self._send_message(connection_id, observer_interest_type)
        await self._listen(websocket)
        await self._close_and_remove_connection(connection_id)

    async def send_message_to_connections(
        self, observer_interest_type: WebSocketObserverInterestType
    ):
        for websocket_id in (self.interested_connections.get(
                observer_interest_type, set())):
            await self._send_message(websocket_id, observer_interest_type)

    def get_connection(self, connection_id: uuid.UUID):
        return self.websocket_manager.get_app_connection(connection_id)

    async def close_connection(self, connection_id: uuid.UUID):
        await self.websocket_manager.close_app_connection(connection_id)
