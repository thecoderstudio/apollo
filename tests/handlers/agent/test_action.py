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


def test_shell_agent_not_found(test_client, session_cookie):
    with pytest.raises(WebSocketDisconnect, match="1013"):
        test_client.websocket_connect(f"/agent/{uuid.uuid4()}/action/linpeas",
                                      cookies=session_cookie)


def test_shell_unauthenticated(test_client):
    with pytest.raises(HTTPException, match="Permission denied."):
        test_client.websocket_connect(f"/agent/{uuid.uuid4()}/action/linpeas")
