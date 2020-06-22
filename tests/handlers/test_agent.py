import uuid

import pytest

from apollo import app
from apollo.lib.websocket_manager import WebSocketManager
from apollo.handlers.agent import close_websocket_connection
from tests import create_http_connection_mock


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
async def test_close_websocket_connect(
        db_session, test_client, access_token, session_cookie,
        authenticated_agent_headers):
    websocket_id = uuid.uuid4()
    websocket_manager = WebSocketManager()

    access_token.access_token = (
        "b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57"
    )
    db_session.commit()

    @app.websocket_route('/websocket_connect', session_cookie)
    async def connect(websocket: WebSocket):
        websocket_manager.connections[websocket_id] = websocket
        await websocket.accept()

    with test_client.websocket_connect('/websocket_connect'):
        http_mock = create_http_connection_mock(headers={
            'authorization': "Bearer b8887eefe2179eccb0565674fe196ee"
            + "12f0621d1d2017a61b195ec17e5d2ac57",
        })
        await close_websocket_connection(http_mock, websocket_id)
        assert len(websocket_manager.connections) == 0

        await websocket_manager.close_and_remove_all_connections()


def test_close_websocket_connect_not_found(test_client, session_cookie):
    response = test_client.get(
        f'ws/{uuid.uuid4()}/close', cookies=session_cookie)

    assert response.status_code == 404


def test_close_websocket_unauthenticated(test_client):
    response = test_client.get(f'ws/{uuid.uuid4()}/close')

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."
