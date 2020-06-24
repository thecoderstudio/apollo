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
        with pytest.raises(KeyError):
            assert user_connection_manager.get_connection(connection_id)


@pytest.mark.asyncio
@pytest.mark.parametrize("closed_connection", [True, False])
async def test_close_connection(mocker, user_connection_manager,
                                closed_connection):
    manager = user_connection_manager

    websocket_mock = mocker.create_autospec(WebSocket)
    connection_id = await manager.websocket_manager.connect_user(
        websocket_mock)

    if closed_connection:
        websocket_mock.send_json.side_effect = RuntimeError(
            'Cannot call "send" once a close message has been sent.'
        )

    await manager.close_connection(connection_id)

    websocket_mock.send_json.assert_awaited_once_with("Closing connection")

    if not closed_connection:
        websocket_mock.close.assert_awaited_once()

    with pytest.raises(KeyError):
        assert manager.get_connection(connection_id)


@pytest.mark.asyncio
@pytest.mark.parametrize("closed_connection", [True, False])
async def test_close_connect_unexpected_runtime_error(
    mocker, user_connection_manager, closed_connection
):
    manager = user_connection_manager

    websocket_mock = mocker.create_autospec(WebSocket)
    connection_id = await manager.websocket_manager.connect_user(
        websocket_mock)

    websocket_mock.send_json.side_effect = RuntimeError('Test unexpected')

    with pytest.raises(RuntimeError, match='Test unexpected'):
        await manager.close_connection(connection_id)

    assert manager.get_connection(connection_id) is websocket_mock


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
