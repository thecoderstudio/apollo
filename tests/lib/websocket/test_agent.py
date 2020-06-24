import uuid
from unittest.mock import patch

import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.websocket.agent import AgentConnectionManager


@pytest.mark.asyncio
async def test_connect(mocker):
    manager = AgentConnectionManager()
    mock_agent_id = uuid.uuid4()
    agent_websocket_mock = mocker.create_autospec(WebSocket)

    mock_user_id = uuid.uuid4()
    agent_websocket_mock.receive_json.side_effect = [
        {
            'connection_id': str(mock_user_id),
            'message': 'test'
        },
        WebSocketDisconnect
    ]

    with patch(
        'apollo.lib.websocket.WebSocketManager.message_user'
    ) as message_user_mock:
        await manager.connect(mock_agent_id, agent_websocket_mock)
        message_user_mock.assert_awaited_once_with(
            mock_user_id, 'test')


@pytest.mark.asyncio
async def test_close_connection(mocker):
    manager = AgentConnectionManager()

    mock_agent_id = uuid.uuid4()
    agent_websocket_mock = mocker.create_autospec(WebSocket)
    await manager.websocket_manager.connect_agent(mock_agent_id,
                                                  agent_websocket_mock)

    await manager.close_connection(mock_agent_id)

    agent_websocket_mock.send_json.assert_awaited_once_with(
        "Closing connection")
    agent_websocket_mock.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_closed_connection(mocker):
    manager = AgentConnectionManager()

    mock_agent_id = uuid.uuid4()
    agent_websocket_mock = mocker.create_autospec(WebSocket)
    await manager.websocket_manager.connect_agent(mock_agent_id,
                                                  agent_websocket_mock)

    agent_websocket_mock.send_json.side_effect = RuntimeError(
        'Cannot call "send" once a close message has been sent.'
    )

    await manager.close_connection(mock_agent_id)

    agent_websocket_mock.send_json.assert_awaited_once_with(
        "Closing connection")


@pytest.mark.asyncio
async def test_close_connect_unexpected_runtime_error(mocker):
    manager = AgentConnectionManager()

    mock_agent_id = uuid.uuid4()
    agent_websocket_mock = mocker.create_autospec(WebSocket)
    await manager.websocket_manager.connect_agent(mock_agent_id,
                                                  agent_websocket_mock)

    agent_websocket_mock.send_json.side_effect = RuntimeError(
        'Test unexpected'
    )

    with pytest.raises(RuntimeError, match='Test unexpected'):
        await manager.close_connection(mock_agent_id)
