import uuid
from unittest.mock import call, patch

import pytest
from starlette.websockets import WebSocketDisconnect

from apollo.lib.exceptions import HTTPException
from apollo.lib.schemas.message import (Command, CommandSchema,
                                        ShellIOSchema)
from apollo.lib.websocket.agent import AgentConnection
from apollo.lib.websocket.interest_type import WebSocketObserverInterestType
from apollo.models.agent import Agent
from apollo.models.oauth import OAuthClient
from tests.lib.websocket import assert_interested_connections_messaged


@pytest.mark.asyncio
@assert_interested_connections_messaged(
    WebSocketObserverInterestType.AGENT_LISTING
)
async def test_post_agent_success(async_test_client, session_cookie):
    response = await async_test_client.post(
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


def test_download_agent(test_client):
    response = test_client.get(
        '/agent/download?target_os=darwin&target_arch=amd64')
    assert response.status_code == 200
    assert response.headers['Content-Disposition'] == (
        'attachment; filename="apollo-agent"')
    assert response.text is not None


@pytest.mark.asyncio
async def test_shell(websocket_mock, test_client, session_cookie,
                     agent_connection_manager):
    connection_id = uuid.uuid4()
    agent_connection = AgentConnection(websocket_mock, uuid.uuid4())
    await agent_connection_manager._accept_connection(agent_connection)

    with patch("apollo.lib.websocket.agent.AgentConnection.send_text",
               wraps=agent_connection.send_text) as send_text:
        with patch('uuid.uuid4', return_value=connection_id):
            with test_client.websocket_connect(
                f"/agent/{agent_connection.id_}/shell",
                cookies=session_cookie
            ) as websocket:
                websocket.send_text("test command")
                websocket.close(code=1000)

        send_text.assert_has_awaits([
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


@pytest.mark.asyncio
async def test_websocket_list_agent_success(db_session, test_client,
                                            session_cookie):
    agent_id_1, agent_id_2 = add_multiple_agents(db_session)
    with test_client.websocket_connect(
            '/agent', cookies=session_cookie) as websocket:
        assert_list_agent_response_data(
            websocket.receive_json(), agent_id_1, agent_id_2)


def test_list_agent_unauthenticated(test_client):
    response = test_client.get('/agent')

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."


def test_websocket_list_agent_unauthenticated(test_client):
    with pytest.raises(HTTPException, match="Permission denied."):
        test_client.websocket_connect("/agent")


def test_list_agent_empty_list(db_session, test_client, session_cookie):
    response = test_client.get('/agent', cookies=session_cookie)

    assert response.json() == []


def test_list_agent_success(db_session, test_client, session_cookie):
    agent_id_1, agent_id_2 = add_multiple_agents(db_session)

    response = test_client.get('/agent', cookies=session_cookie)
    response_body = response.json()

    assert response.status_code == 200
    assert_list_agent_response_data(response_body, agent_id_1, agent_id_2)


def assert_list_agent_response_data(data, agent_id_1, agent_id_2):
    assert len(data) == 2

    agent_data = data[0]
    assert agent_data['name'] in ['test', 'test2']
    assert agent_data['id'] in [str(agent_id_1), str(agent_id_2)]
    assert agent_data['connection_state'] == 'disconnected'
    assert agent_data['external_ip_address'] == '0.0.0.0'
    assert agent_data['operating_system'] == 'darwin'
    assert agent_data['architecture'] == 'amd64'


def add_multiple_agents(db_session):
    agent_id_1 = uuid.uuid4()
    agent_id_2 = uuid.uuid4()
    platform_info = {
        'external_ip_address': '0.0.0.0',
        'operating_system': 'darwin',
        'architecture': 'amd64'
    }

    agent = Agent(
        id=agent_id_1,
        name='test',
        oauth_client=OAuthClient(type='confidential'),
        **platform_info
    )
    agent_2 = Agent(
        id=agent_id_2,
        name='test2',
        oauth_client=OAuthClient(type='confidential'),
        **platform_info
    )
    db_session.add(agent)
    db_session.add(agent_2)
    db_session.commit()

    return agent_id_1, agent_id_2
