import json
import uuid
from typing import Dict, Set

from fastapi import WebSocket
from pydantic.json import pydantic_encoder

from apollo.lib.singleton import Singleton
from apollo.lib.websocket.connection import Connection, ConnectionManager
from apollo.lib.websocket.interest_type import WebSocketObserverInterestType


class AppConnectionManager(ConnectionManager, metaclass=Singleton):
    connections = ConnectionManager.websocket_manager.open_app_connections
    interested_connections: Dict[WebSocketObserverInterestType,
                                 Set[uuid.UUID]] = {}

    async def connect(
        self, websocket: WebSocket,
        observer_interest_type: WebSocketObserverInterestType
    ):
        connection = AppConnection(websocket)
        await self._accept_connection(connection)
        self._add_interested_connection(observer_interest_type, connection.id_)
        await self._send_message(connection.id_, observer_interest_type)
        async for _ in connection.listen():
            pass

        self._remove_connection(connection)
        return connection

    def _add_interested_connection(
        self,
        observer_interest_type: WebSocketObserverInterestType,
        connection_id: uuid.UUID
    ):
        connections = self.interested_connections.get(observer_interest_type,
                                                      set())
        connections.add(connection_id)
        self.interested_connections[observer_interest_type] = connections

    async def _send_message(
        self, websocket_id: uuid.UUID,
        observer_interest_type: WebSocketObserverInterestType
    ):
        await self.get_connection(websocket_id).send_text(json.dumps(
            observer_interest_type.run_corresponding_function(),
            default=pydantic_encoder
        ))

    def _remove_connection(self, connection: Connection):
        for connection_set in self.interested_connections.values():
            connection_set.discard(connection.id_)
        super()._remove_connection(connection)

    async def message_interested_connections(
        self, observer_interest_type: WebSocketObserverInterestType
    ):
        for websocket_id in (self.interested_connections.get(
                observer_interest_type, set())):
            await self._send_message(websocket_id, observer_interest_type)


class AppConnection(Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, id_=uuid.uuid4(), **kwargs)
