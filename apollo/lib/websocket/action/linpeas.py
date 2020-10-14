import logging
import uuid

from fastapi import WebSocket

from apollo.lib.redis import RedisSession
from apollo.lib.websocket.user import (UserCommandConnectionManager,
                                       UserConnection)

REPORT_CACHE_TTL_IN_SECONDS = 1800
REPORT_CACHE_KEY_FORMAT = "linpeas_{target_agent_id}"


class LinPEASConnection(UserConnection):
    total_report = ""

    def __init__(self, manager: 'LinPEASManager', target_agent_id: uuid.UUID,
                 *args, **kwargs):
        super().__init__(manager, *args, **kwargs)
        self.target_agent_id = target_agent_id

    async def send_text(self, text: str):
        await super().send_text(text)
        self.total_report += text

    def persist_report(self):
        RedisSession().write_to_cache(
            REPORT_CACHE_KEY_FORMAT.format(
                target_agent_id=self.target_agent_id
            ),
            self.total_report,
            REPORT_CACHE_TTL_IN_SECONDS
        )


class LinPEASManager(UserCommandConnectionManager):
    def _create_user_connection(
        self,
        websocket: WebSocket,
        target_agent_id: uuid.UUID
    ):
        return LinPEASConnection(self, target_agent_id, websocket)

    @classmethod
    async def _close_connection(cls, connection: LinPEASConnection):
        await super()._close_connection(connection)
        connection.persist_report()

    @staticmethod
    def get_report(target_agent_id: uuid.UUID):
        return RedisSession().get_from_cache(
            REPORT_CACHE_KEY_FORMAT.format(target_agent_id=target_agent_id)
        )
