import uuid
from unittest.mock import call, patch

import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.exceptions import HTTPException
from apollo.lib.schemas.message import (Command, CommandSchema,
                                        ShellIOSchema)
from apollo.models.agent import Agent
from apollo.models.oauth import OAuthClient


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
async def test_shell(mocker, test_client, session_cookie, websocket_manager):
    connection_id = uuid.uuid4()
    mock_agent_id = uuid.uuid4()
    agent_websocket_mock = mocker.create_autospec(WebSocket)
    await websocket_manager.connect_agent(mock_agent_id, agent_websocket_mock)

    with patch('uuid.uuid4', return_value=connection_id):
        with test_client.websocket_connect(
            f"/agent/{mock_agent_id}/shell",
            cookies=session_cookie
        ) as websocket:
            websocket.send_text("test command")
            websocket.close(code=1000)

    agent_websocket_mock.send_text.assert_has_awaits([
        call(CommandSchema(
            connection_id=connection_id,
            command=Command.NEW_CONNECTION
        ).json()),
        call(ShellIOSchema(
            connection_id=connection_id,
            message="test command"
        ).json())
    ])


def test_shell_agent_not_found(test_client, session_cookie):
    with pytest.raises(WebSocketDisconnect, match="1013"):
        test_client.websocket_connect(f"/agent/{uuid.uuid4()}/shell",
                                      cookies=session_cookie)


def test_shell_unauthenticated(test_client):
    with pytest.raises(HTTPException, match="Permission denied."):
        test_client.websocket_connect(f"/agent/{uuid.uuid4()}/shell")


def test_list_agent_empty_list(db_session, test_client, session_cookie):
    response = test_client.get('/agent', cookies=session_cookie)

    assert response.json() == []


def test_list_agent_success(db_session, test_client, session_cookie):
    agent_id_1 = uuid.uuid4()
    agent_id_2 = uuid.uuid4()
    agent = Agent(id=agent_id_1, name='test',
                  oauth_client=OAuthClient(type='confidential'))
    agent_2 = Agent(id=agent_id_2, name='test2',
                    oauth_client=OAuthClient(type='confidential'))
    db_session.add(agent)
    db_session.add(agent_2)
    db_session.commit()

    response = test_client.get('/agent', cookies=session_cookie)
    response_body = response.json()

    assert response.status_code == 200
    assert len(response_body) == 2

    agent_data = response_body[0]
    assert agent_data['name'] in ['test', 'test2']
    assert agent_data['id'] in [str(agent_id_1), str(agent_id_2)]
    assert agent_data['connection_state'] == 'disconnected'


def test_list_agent_unauthenticated(test_client):
    response = test_client.get('/agent')

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."
