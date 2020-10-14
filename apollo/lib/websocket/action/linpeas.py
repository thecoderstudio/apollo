import logging

from fastapi import WebSocket

from apollo.lib.websocket.user import (UserCommandConnectionManager,
                                       UserConnection)


class LinPEASManager(UserCommandConnectionManager):
    @staticmethod
    def _create_user_connection(websocket: WebSocket):
        return LinPEASConnection(websocket)


class LinPEASConnection(UserConnection):
    async def send_text(self, text: str):
        await super().send_text(text)
