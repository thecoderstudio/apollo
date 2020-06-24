import uuid
from unittest.mock import patch

import pytest
from fastapi import WebSocket

from apollo.lib.exceptions import HTTPException
from apollo.lib.websocket import WebSocketManager


def test_post_agent_success(test_client, session_cookie):
    response = test_client.post(
        '/agent',
        json={'name': 'test'},
        cookies=session_cookie
    )
    agent = response.json()
    oauth_client = agent['oauth_client']

    assert response.status_code == 201
    assert agent['id'] is not None
    assert oauth_client['agent_id'] is not None
    assert oauth_client['secret'] is not None
    assert oauth_client['type'] == 'confidential'


def test_post_agent_name_exists(test_client, session_cookie):
    agent = {'name': 'test'}
    test_client.post('/agent', json=agent, cookies=session_cookie)
    response = test_client.post('/agent', json=agent)

    assert response.status_code == 400


def test_post_agent_unauthenticated(test_client, db_session):
    response = test_client.post(
        '/agent',
        json={'name': 'test'}
    )

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."


@pytest.mark.asyncio
async def test_shell(mocker, test_client, session_cookie):
    connection_id = uuid.uuid4()
    mock_agent_id = uuid.uuid4()
    agent_websocket_mock = mocker.create_autospec(WebSocket)
    await WebSocketManager().connect_agent(mock_agent_id, agent_websocket_mock)

    with patch('uuid.uuid4', return_value=connection_id):
        with test_client.websocket_connect(
            f"/agent/{mock_agent_id}/shell",
            cookies=session_cookie
        ) as websocket:
            websocket.send_text("test command")
            websocket.close(code=1000)

    agent_websocket_mock.send_json.assert_awaited_once_with({
        'connection_id': str(connection_id),
        'message': "test command"
    })


def test_shell_agent_not_found(test_client, session_cookie):
    with pytest.raises(HTTPException) as e:
        test_client.websocket_connect(f"/agent/{uuid.uuid4()}/shell",
                                      cookies=session_cookie)
        assert e.status_code == 404


def test_shell_unauthenticated(test_client):
    with pytest.raises(HTTPException, match="Permission denied."):
        test_client.websocket_connect(f"/agent/{uuid.uuid4()}/shell")
