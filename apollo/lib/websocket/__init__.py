import uuid
from typing import Dict

from apollo.lib.singleton import Singleton


class WebSocketManager(metaclass=Singleton):
    agent_connections: Dict[uuid.UUID, 'Connection'] = {}
    open_app_connections: Dict[uuid.UUID, 'Connection'] = {}
    open_user_connections: Dict[uuid.UUID, 'Connection'] = {}
