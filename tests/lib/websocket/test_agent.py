import uuid
from unittest.mock import patch

import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.websocket.agent import AgentConnectionManager


@pytest.mark.asyncio
async def test_agent_connection_manager_connect(mocker):
    manager = AgentConnectionManager()

    mock_agent_id = uuid.uuid4()
    agent_websocket_mock = mocker.create_autospec(WebSocket)
    await manager.websocket_manager.connect_agent(mock_agent_id,
                                                  agent_websocket_mock)

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
