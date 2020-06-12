from tests.asserts import raisesHTTPForbidden

import pytest
from apollo.lib.websocket_manager import WebSocketManager


@pytest.mark.asyncio
async def test_shell(test_client, authenticated_agent_headers):
    with test_client.websocket_connect(
        '/ws', headers=authenticated_agent_headers
    ) as websocket:
        assert websocket.receive_json() == "Connection accepted"

    websocket_manager = WebSocketManager()
    await websocket_manager.close_and_remove_all_connections()


def test_shell_unauthenticated(test_client):
    with raisesHTTPForbidden:
        test_client.websocket_connect('/ws')


