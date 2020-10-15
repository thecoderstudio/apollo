import re
import uuid

from fastapi import WebSocket

from apollo.lib.redis import RedisSession
from apollo.lib.schemas.message import Command
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, command=Command.LINPEAS, **kwargs)

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

    @classmethod
    def get_report(cls, target_agent_id: uuid.UUID, ansi: bool = False):
        report = RedisSession().get_from_cache(
            REPORT_CACHE_KEY_FORMAT.format(target_agent_id=target_agent_id)
        )
        if not report:
            return None

        if not ansi:
            return cls._filter_ansi_escape_codes(report)

        return report

    @staticmethod
    def _filter_ansi_escape_codes(data: str):
        ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        return ansi_escape.sub('', data)
