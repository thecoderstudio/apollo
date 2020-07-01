import uuid
from unittest.mock import patch

import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.websocket.app import WebSocketObserverInterestTypes

def test_websocket_observer_interest_types():
     pass

# @pytest.mark.asyncio
# async def test_connect_and_send(mocker, app_connection_manager):
#
#     app_websocket_mock = mocker.create_autospec(WebSocket)
#     app_websocket_mock.receive_text.side_effect = [
#         "message",
#         WebSocketDisconnect
#     ]
#     with patch(
#         'apollo.lib.websocket.app.fastapi.WebSocket.send_json'
#     ) as send_json_mock:
#         await app_connection_manager.connect_and_send(
#             app_websocket_mock,
#             WebSocketObserverInterestTypes.AGENT_LISTING
#         )
#         send_json_mock.assert_awaited_once()

@pytest.mark.asyncio
async def test_send_message_to_connections():
    pass

def test_close_connection():
    pass