import uuid
from unittest.mock import call, patch

import pytest
from starlette.websockets import WebSocketDisconnect

from apollo.lib.exceptions import HTTPException
from apollo.lib.schemas.message import Command, CommandSchema
from apollo.lib.websocket.agent import AgentConnection


@pytest.mark.asyncio
async def test_linpeas_success(agent_connection_manager, websocket_mock,
                               session_cookie, test_client):
    connection_id = uuid.uuid4()
    agent_connection = AgentConnection(websocket_mock, uuid.uuid4())
    await agent_connection_manager._accept_connection(agent_connection)

    with patch(
        'apollo.lib.websocket.agent.AgentConnection.send_text',
        wraps=agent_connection.send_text
    ) as send_text:
        with patch('uuid.uuid4', return_value=connection_id):
            with test_client.websocket_connect(
                f"/agent/{agent_connection.id_}/action/linpeas",
                cookies=session_cookie
            ) as websocket:
                websocket.close(code=1000)

        send_text.assert_has_awaits([
            call(CommandSchema(
                connection_id=connection_id,
                command=Command.NEW_CONNECTION
            ).json()),
            call(CommandSchema(
                connection_id=connection_id,
                command=Command.LINPEAS
            ).json())
        ])


def test_linpeas_agent_not_found(test_client, session_cookie):
    with pytest.raises(WebSocketDisconnect, match="1013"):
        test_client.websocket_connect(f"/agent/{uuid.uuid4()}/action/linpeas",
                                      cookies=session_cookie)


def test_linpeas_unauthenticated(test_client):
    with pytest.raises(HTTPException, match="Permission denied."):
        test_client.websocket_connect(f"/agent/{uuid.uuid4()}/action/linpeas")


def test_linpeas_export_success(session_cookie, test_client, access_token):
    agent_id = access_token.client.agent_id

    with patch('apollo.lib.redis.RedisSession.get_from_cache',
               return_value='\x1b[1;32mab\x1b[0m'):
        response = test_client.get(
            f"/agent/{agent_id}/action/linpeas/export",
            cookies=session_cookie
        )

        assert response.status_code == 200
        assert response.text == 'ab'
        assert response.headers['Content-Disposition'] == (
            "attachment; filename=LinPEAS-test.txt")


def test_linpeas_export_success_ansi(session_cookie, test_client,
                                     access_token):
    agent_id = access_token.client.agent_id

    with patch('apollo.lib.redis.RedisSession.get_from_cache',
               return_value='\x1b[1;32mab\x1b[0m'):
        response = test_client.get(
            f"/agent/{agent_id}/action/linpeas/export?ansi=true",
            cookies=session_cookie
        )

        assert response.status_code == 200
        assert response.text == '\x1b[1;32mab\x1b[0m'


def test_linpeas_export_success_custom_filename(session_cookie, test_client,
                                                access_token):
    agent_id = access_token.client.agent_id

    with patch('apollo.lib.redis.RedisSession.get_from_cache',
               return_value='\x1b[1;32mab\x1b[0m'):
        response = test_client.get(
            f"/agent/{agent_id}/action/linpeas/export?filename='custom.txt'",
            cookies=session_cookie
        )

        assert response.status_code == 200
        assert response.text == 'ab'
        assert response.headers['Content-Disposition'] == (
            "attachment; filename='custom.txt'")


def test_linpeas_export_agent_not_found(test_client, session_cookie):
    response = test_client.get(
        f"/agent/{uuid.uuid4()}/action/linpeas/export",
        cookies=session_cookie
    )

    assert response.status_code == 404
    assert response.json()['detail'] == "No LinPEAS report found."


def test_linpeas_export_unauthenticated(test_client):
    response = test_client.get(
        f"/agent/{uuid.uuid4()}/action/linpeas/export")

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."
