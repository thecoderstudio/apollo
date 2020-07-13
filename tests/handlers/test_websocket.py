import pytest

from tests.asserts import raisesHTTPForbidden


@pytest.mark.asyncio
async def test_connect(test_client, authenticated_agent_headers):
    with test_client.websocket_connect(
        '/ws', headers=authenticated_agent_headers
    ) as websocket:
        websocket.close(code=1000)


def test_connect_unauthenticated(test_client):
    with raisesHTTPForbidden:
        test_client.websocket_connect('/ws')
