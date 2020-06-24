import uuid

import pytest

from apollo.lib.exceptions import HTTPException


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


def test_shell(test_client, session_cookie):
    pass


def test_shell_agent_not_found(test_client, session_cookie):
    with pytest.raises(HTTPException) as e:
        test_client.websocket_connect(f"/agent/{uuid.uuid4()}/shell",
                                      cookies=session_cookie)
        assert e.status_code == 404


def test_shell_unauthenticated(test_client):
    with pytest.raises(HTTPException, match="Permission denied."):
        test_client.websocket_connect(f"/agent/{uuid.uuid4()}/shell")
