from tests.asserts import raisesHTTPForbidden

import pytest

from apollo.lib.websocket import WebSocketManager


@pytest.mark.asyncio
async def test_connect(test_client, authenticated_agent_headers):
    with test_client.websocket_connect(
        '/ws', headers=authenticated_agent_headers
    ) as websocket:
        assert websocket.receive_json() == "Connection accepted"
        websocket.close(code=1000)


def test_connect_unauthenticated(test_client):
    with raisesHTTPForbidden:
        test_client.websocket_connect('/ws')
