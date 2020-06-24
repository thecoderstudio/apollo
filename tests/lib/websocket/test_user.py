import uuid
from unittest.mock import patch

import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.websocket.user import UserConnectionManager


@pytest.mark.asyncio
async def test_user_connection_manager_connect(mocker):
    manager = UserConnectionManager()
    mock_agent_id = uuid.uuid4()

    user_websocket_mock = mocker.create_autospec(WebSocket)
    user_websocket_mock.receive_text.side_effect = ["test",
                                                    WebSocketDisconnect]
    with patch(
        'apollo.lib.websocket.WebSocketManager.message_agent'
    ) as message_agent_mock:
        connection_id = await manager.connect(
            user_websocket_mock, mock_agent_id)
        message_agent_mock.assert_awaited_once_with(
            connection_id, mock_agent_id, 'test')


@pytest.mark.asyncio
async def test_user_connection_manager_get_connection(mocker):
    manager = UserConnectionManager()
    websocket_mock = mocker.create_autospec(WebSocket)
    connection_id = await manager.websocket_manager.connect_user(
        websocket_mock)

    assert manager.get_connection(connection_id) is websocket_mock


def test_user_connection_manager_get_connection_not_found():
    manager = UserConnectionManager()

    with pytest.raises(KeyError):
        manager.get_connection(uuid.uuid4())
