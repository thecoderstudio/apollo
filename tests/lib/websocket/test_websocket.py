import uuid

import pytest

from apollo.lib.websocket import WebSocketManager


@pytest.mark.asyncio
async def test_connect_agent(mocker):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)
    mock_agent_id = uuid.uuid4()
    manager = WebSocketManager()

    await manager.connect_agent(mock_agent_id, websocket_mock)

    assert manager.open_agent_connections[mock_agent_id] == websocket_mock
    websocket_mock.accept.assert_awaited_once()
