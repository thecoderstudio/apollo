import uuid
from unittest.mock import call, patch

import pytest
from starlette.websockets import WebSocketDisconnect, WebSocketState

from apollo.lib.schemas.message import ShellIOSchema
from apollo.lib.websocket.agent import AgentConnection
from apollo.lib.websocket.user import UserConnection


@pytest.mark.asyncio
async def test_agent_connection_manager_get_connection(
    agent_connection_manager,
    websocket_mock
):
    agent_id = uuid.uuid4()
    agent_connection = AgentConnection(websocket_mock, agent_id)
    await agent_connection_manager.accept_connection(agent_connection)
    fetched_connection = agent_connection_manager.get_connection(agent_id)

    assert agent_connection is fetched_connection


@pytest.mark.asyncio
async def test_agent_connection_manager_connect(
    agent_connection_manager,
    user_connection_manager,
    websocket_mock
):
    agent_id = uuid.uuid4()

    user_connection = UserConnection(websocket_mock)
    await user_connection_manager.accept_connection(user_connection)

    with patch(
        'apollo.lib.websocket.agent.AgentConnection.receive_json',
        side_effect=[
            ShellIOSchema(
                connection_id=user_connection.id_,
                message='a'
            ).dict(),
            ShellIOSchema(
                connection_id=user_connection.id_,
                message='b'
            ).dict(),
            WebSocketDisconnect
        ]
    ):
        with patch(
            'apollo.lib.websocket.user.UserConnection.send_text',
            wraps=user_connection.send_text
        ) as send_text:
            await agent_connection_manager.connect(agent_id, websocket_mock)

            send_text.assert_has_awaits([call('a'), call('b')])

    assert agent_connection_manager.get_connection(
        agent_id
    )is not None


@pytest.mark.asyncio
async def test_agent_connection_manager_close_connection(
    agent_connection_manager,
    websocket_mock
):
    pass


@pytest.mark.asyncio
async def test_agent_connection_manager_close_all_connections(
    agent_connection_manager,
    websocket_mock
):
    pass
