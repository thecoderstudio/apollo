import uuid
from unittest.mock import call, patch

import pytest
from starlette.websockets import WebSocketDisconnect, WebSocketState

from apollo.lib.schemas.message import (BaseMessageSchema, ServerCommand,
                                        ServerCommandSchema, ShellIOSchema)
from apollo.lib.websocket.agent import AgentConnection
from apollo.lib.websocket.interest_type import WebSocketObserverInterestType
from apollo.lib.websocket.user import UserConnection
from tests.lib.websocket import assert_interested_connections_messaged


@pytest.mark.asyncio
async def test_agent_connection_manager_get_connection(
    agent_connection_manager,
    websocket_mock
):
    agent_id = uuid.uuid4()
    agent_connection = AgentConnection(websocket_mock, agent_id)
    await agent_connection_manager._accept_connection(agent_connection)
    fetched_connection = agent_connection_manager.get_connection(agent_id)

    assert agent_connection is fetched_connection


@pytest.mark.asyncio
@pytest.mark.parametrize('existing_agent', [True, False])
async def test_agent_connection_manager_connect(
    agent_connection_manager,
    user_shell_connection_manager,
    websocket_mock,
    existing_agent
):
    agent_id = uuid.uuid4()

    if existing_agent:
        await agent_connection_manager._accept_connection(AgentConnection(
            websocket_mock, agent_id))

    user_connection = UserConnection(user_shell_connection_manager,
                                     websocket_mock)
    await user_shell_connection_manager._accept_connection(user_connection)

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
    ) is not None


@pytest.mark.asyncio
async def test_agent_connection_manager_close_connection(
    agent_connection_manager,
    websocket_mock
):
    agent_connection = AgentConnection(websocket_mock, uuid.uuid4())
    await agent_connection_manager._accept_connection(agent_connection)

    await agent_connection_manager.close_connection(agent_connection.id_)

    assert agent_connection.application_state is WebSocketState.DISCONNECTED


@pytest.mark.asyncio
async def test_agent_connection_manager_close_all_connections(
    agent_connection_manager,
    websocket_mock
):
    agent_ids = [uuid.uuid4() for _ in range(0, 3)]
    for agent_id in agent_ids:
        agent_connection = AgentConnection(websocket_mock, agent_id)
        await agent_connection_manager._accept_connection(agent_connection)

    await agent_connection_manager.close_all_connections()

    for agent_id in agent_ids:
        agent_connection = agent_connection_manager.get_connection(agent_id)
        assert (agent_connection.application_state is
                WebSocketState.DISCONNECTED)


@pytest.mark.asyncio
async def test_agent_connection_message(websocket_mock):
    message = BaseMessageSchema(connection_id=uuid.uuid4())
    connection = AgentConnection(websocket_mock, uuid.uuid4())
    await connection.accept()

    with patch('apollo.lib.websocket.agent.AgentConnection.send_text',
               wraps=connection.send_text) as send_text:
        await connection.message(message)

        send_text.assert_awaited_once_with(message.json())


@pytest.mark.asyncio
async def test_agent_connection_listen_and_forward(
    user_command_connection_manager,
    websocket_mock
):
    user_connection = UserConnection(user_command_connection_manager,
                                     websocket_mock)
    await user_command_connection_manager._accept_connection(user_connection)
    agent_connection = AgentConnection(websocket_mock, uuid.uuid4())

    server_command = ServerCommandSchema(
        connection_id=user_connection.id_,
        command=ServerCommand.FINISHED
    )

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
            server_command.dict(),
            WebSocketDisconnect
        ]
    ):
        with patch(
            'apollo.lib.websocket.user.UserConnection.send_text',
            wraps=user_connection.send_text
        ) as send_text:
            with patch(
                'apollo.lib.websocket.user.UserCommandConnectionManager.'
                'process_server_command'
            ) as send_command:
                await agent_connection.listen_and_forward()

                send_text.assert_has_awaits([call('a'), call('b')])
                send_command.assert_awaited_with(server_command)


@pytest.mark.asyncio
@assert_interested_connections_messaged(
    WebSocketObserverInterestType.AGENT_LISTING
)
async def test_agent_connection_accept(websocket_mock):
    connection = AgentConnection(websocket_mock, uuid.uuid4())
    await connection.accept()

    assert connection.application_state is WebSocketState.CONNECTED


@pytest.mark.asyncio
@assert_interested_connections_messaged(
    WebSocketObserverInterestType.AGENT_LISTING
)
async def test_agent_connection_close(websocket_mock):
    connection = AgentConnection(websocket_mock, uuid.uuid4())
    await connection.accept()
    await connection.close()

    assert connection.application_state is WebSocketState.DISCONNECTED
