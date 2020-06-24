import uuid
from unittest.mock import patch

import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


@pytest.mark.asyncio
async def test_connect(mocker, user_connection_manager):
    mock_agent_id = uuid.uuid4()

    user_websocket_mock = mocker.create_autospec(WebSocket)
    user_websocket_mock.receive_text.side_effect = ["test",
                                                    WebSocketDisconnect]
    with patch(
        'apollo.lib.websocket.WebSocketManager.message_agent'
    ) as message_agent_mock:
        connection_id = await user_connection_manager.connect(
            user_websocket_mock, mock_agent_id)
        message_agent_mock.assert_awaited_once_with(
            connection_id, mock_agent_id, 'test')


@pytest.mark.asyncio
async def test_get_connection(mocker, user_connection_manager):
    websocket_mock = mocker.create_autospec(WebSocket)
    connection_id = await (
        user_connection_manager.websocket_manager.connect_user(websocket_mock)
    )

    assert (user_connection_manager.get_connection(connection_id) is
            websocket_mock)


def test_get_connection_not_found(user_connection_manager):
    with pytest.raises(KeyError):
        user_connection_manager.get_connection(uuid.uuid4())
