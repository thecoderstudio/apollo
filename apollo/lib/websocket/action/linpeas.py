import logging

from fastapi import WebSocket

from apollo.lib.websocket.user import (UserCommandConnectionManager,
                                       UserConnection)


class LinPEASConnection(UserConnection):
    total_report = ""

    async def send_text(self, text: str):
        await super().send_text(text)
        self.total_report += text


class LinPEASManager(UserCommandConnectionManager):
    def _create_user_connection(self, websocket: WebSocket):
        return LinPEASConnection(self, websocket)

    @classmethod
    async def _close_connection(cls, connection: LinPEASConnection):
        await super()._close_connection(connection)
        logging.critical(len(
            connection.total_report.encode('utf-8')
        ))
