import uuid
from unittest.mock import call, patch

import pytest
from starlette.websockets import WebSocketDisconnect, WebSocketState

from apollo.lib.schemas.message import (Command, CommandSchema, ServerCommand,
                                        ServerCommandSchema, ShellIOSchema)
from apollo.lib.websocket.agent import AgentConnection
from apollo.lib.websocket.user import UserConnection, TRY_AGAIN_LATER


def test_user_connection_random_id_on_construction(websocket_mock):
    a = UserConnection(websocket_mock)
    b = UserConnection(websocket_mock)
    assert a.id_ != b.id_


@pytest.mark.asyncio
async def test_user_connection_manager_get_connection(
    user_connection_manager,
    websocket_mock
):
    user_connection = UserConnection(websocket_mock)
    await user_connection_manager._accept_connection(user_connection)
    fetched_connection = user_connection_manager.get_connection(
        user_connection.id_)

    assert user_connection is fetched_connection


@pytest.mark.asyncio
async def test_user_connection_manager_abstract(
    agent_connection_manager,
    user_connection_manager,
    websocket_mock
):
    agent_connection = AgentConnection(websocket_mock, uuid.uuid4())
    await agent_connection_manager._accept_connection(agent_connection)

    with pytest.raises(NotImplementedError):
        await user_connection_manager.connect(
            websocket_mock,
            agent_connection.id_
        )


@pytest.mark.asyncio
async def test_send_message_to_non_existent_user_connection(
    user_connection_manager
):
    message = ShellIOSchema(
        connection_id=uuid.uuid4(),
        message="test"
    )

    with patch('apollo.lib.websocket.user.logging.critical') as logging_mock:
        sent = await user_connection_manager.send_message(message)
        assert sent is False
        logging_mock.assert_called_once_with(f"message dropped: {message}")


@pytest.mark.asyncio
async def test_user_shell_connection_manager_connect(
    agent_connection_manager,
    user_shell_connection_manager,
    websocket_mock
):
    agent_connection = AgentConnection(websocket_mock, uuid.uuid4())
    await agent_connection_manager._accept_connection(agent_connection)

    with patch(
        'apollo.lib.websocket.agent.AgentConnection.send_text',
        wraps=agent_connection.send_text
    ) as send_text:
        with patch(
            'apollo.lib.websocket.user.UserConnection.receive_text',
            side_effect=['a', 'b', WebSocketDisconnect]
        ):
            user_connection = await user_shell_connection_manager.connect(
                websocket_mock,
                agent_connection.id_
            )
            connection_id = user_connection.id_

            send_text.assert_has_awaits([
                call(CommandSchema(
                    connection_id=connection_id,
                    command=Command.NEW_CONNECTION
                ).json()),
                call(ShellIOSchema(
                    connection_id=connection_id,
                    message="a"
                ).json()),
                call(ShellIOSchema(
                    connection_id=connection_id,
                    message="b"
                ).json()),
            ])

    assert isinstance(user_connection, UserConnection)
    with pytest.raises(KeyError):
        user_shell_connection_manager.get_connection(connection_id)


@pytest.mark.asyncio
async def test_user_command_connection_manager_connect(
    agent_connection_manager,
    user_command_connection_manager,
    websocket_mock
):
    user_command_connection_manager.command = Command.LINPEAS
    agent_connection = AgentConnection(websocket_mock, uuid.uuid4())
    await agent_connection_manager._accept_connection(agent_connection)

    with patch(
        'apollo.lib.websocket.agent.AgentConnection.send_text',
        wraps=agent_connection.send_text
    ) as send_text:
        user_connection = await user_command_connection_manager.connect(
            websocket_mock,
            agent_connection.id_
        )
        connection_id = user_connection.id_
        await user_command_connection_manager.process_server_command(
            ServerCommandSchema(
                connection_id=connection_id,
                command=ServerCommand.FINISHED
            )
        )

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

    assert isinstance(user_connection, UserConnection)
    with pytest.raises(KeyError):
        user_command_connection_manager.get_connection(connection_id)


@pytest.mark.asyncio
async def test_user_connection_manager_connect_active_agent_not_found(
    agent_connection_manager,
    user_connection_manager,
    websocket_mock
):
    agent_connection = AgentConnection(websocket_mock, uuid.uuid4())
    await agent_connection_manager._accept_connection(agent_connection)
    agent_connection.client_state = WebSocketState.DISCONNECTED

    user_connection = await user_connection_manager.connect(
        websocket_mock,
        agent_connection.id_
    )

    assert user_connection is None
    websocket_mock.close.assert_awaited_once_with(code=TRY_AGAIN_LATER)
