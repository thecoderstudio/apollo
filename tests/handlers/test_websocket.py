from unittest.mock import patch

import pytest

from apollo.models.agent import get_agent_by_id
from tests.asserts import raisesHTTPForbidden


@pytest.mark.asyncio
async def test_connect(test_client, authenticated_agent_headers, db_session,
                       access_token):
    headers = {
        'user-agent': "Apollo Agent - darwin/amd64",
        **authenticated_agent_headers
    }

    with patch('fastapi.WebSocket.client') as client_mock:
        client_mock.host = '0.0.0.0'
        with test_client.websocket_connect(
            '/ws', headers=headers,
        ) as websocket:
            websocket.close(code=1000)

    agent = get_agent_by_id(db_session, access_token.client_id)
    assert agent.operating_system == 'darwin'
    assert agent.architecture == 'amd64'


@pytest.mark.asyncio
async def test_connect_invalid_user_agent(
    test_client,
    authenticated_agent_headers,
    db_session,
    access_token
):
    headers = {
        'user-agent': "fake",
        **authenticated_agent_headers
    }

    with patch('apollo.handlers.websocket.logging.error') as log_mock:
        with patch('fastapi.WebSocket.client') as client_mock:
            client_mock.host = '0.0.0.0'
            with test_client.websocket_connect(
                '/ws', headers=headers,
            ) as websocket:
                websocket.close(code=1000)

        log_mock.assert_called_once()

    agent = get_agent_by_id(db_session, access_token.client_id)
    assert agent.operating_system is None
    assert agent.architecture is None


def test_connect_unauthenticated(test_client):
    with raisesHTTPForbidden:
        test_client.websocket_connect('/ws')
