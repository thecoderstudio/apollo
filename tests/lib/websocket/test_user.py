import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.websocket.user import UserConnectionManager


@pytest.mark.asyncio
async def test_user_connection_manager_connect(mocker):
    manager = UserConnectionManager()
    mock_agent_id = uuid.uuid4()
    agent_websocket_mock = AsyncMock(spec=WebSocket)
    await manager.websocket_manager.connect_agent(mock_agent_id,
                                                  agent_websocket_mock)

    user_websocket_mock = AsyncMock(spec=WebSocket)
    user_websocket_mock.receive_text.side_effect = ["test",
                                                    WebSocketDisconnect]
    with patch(
        'apollo.lib.websocket.WebSocketManager.message_agent'
    ) as message_agent_mock:
        connection_id = await manager.connect(
            user_websocket_mock, mock_agent_id)
        message_agent_mock.assert_awaited_once_with(
            connection_id, mock_agent_id, 'test')
