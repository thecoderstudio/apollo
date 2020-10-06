import uuid
from unittest.mock import call, patch

import click
import pytest
from starlette.websockets import WebSocketDisconnect

from apollo.lib.exceptions.websocket import SendAfterConnectionClosure
from apollo.lib.schemas.message import Command, CommandSchema, ShellIOSchema
from apollo.lib.websocket.agent import AgentConnection
from apollo.lib.websocket.shell import ShellConnection
from apollo.lib.websocket.user import UserConnection


@pytest.mark.asyncio
async def test_shell_connection_start(mocker, websocket_mock):
    agent_connection = AgentConnection(websocket_mock, uuid.uuid4())
    user_connection = UserConnection(websocket_mock)
    await agent_connection.accept()
    await user_connection.accept()

    send_text = mocker.patch(
        'apollo.lib.websocket.agent.AgentConnection.send_text',
        wraps=agent_connection.send_text
    )

    shell_connection = await ShellConnection.start(user_connection,
                                                   agent_connection)

    send_text.assert_awaited_once_with(CommandSchema(
        connection_id=user_connection.id_,
        command=Command.NEW_CONNECTION
    ).json())

    assert shell_connection.origin is user_connection
    assert shell_connection.target is agent_connection


@pytest.mark.asyncio
async def test_shell_connection_send_command(mocker, websocket_mock):
    agent_connection = AgentConnection(websocket_mock, uuid.uuid4())
    user_connection = UserConnection(websocket_mock)
    await agent_connection.accept()
    await user_connection.accept()

    send_text = mocker.patch(
        'apollo.lib.websocket.agent.AgentConnection.send_text',
        wraps=agent_connection.send_text
    )
    shell_connection = await ShellConnection.start(user_connection,
                                                   agent_connection)
    await shell_connection.send_command(Command.LINPEAS)

    send_text.assert_has_awaits([
        call(CommandSchema(
            connection_id=user_connection.id_,
            command=Command.NEW_CONNECTION
        ).json()),
        call(CommandSchema(
            connection_id=user_connection.id_,
            command=Command.LINPEAS
        ).json())
    ])


@pytest.mark.asyncio
async def test_shell_connection_listen_and_forward(mocker, websocket_mock):
    agent_connection = AgentConnection(websocket_mock, uuid.uuid4())
    user_connection = UserConnection(websocket_mock)
    await agent_connection.accept()
    await user_connection.accept()
    shell_connection = await ShellConnection.start(user_connection,
                                                   agent_connection)

    send_text = mocker.patch(
        'apollo.lib.websocket.agent.AgentConnection.send_text',
        wraps=agent_connection.send_text
    )
    mocker.patch(
        'apollo.lib.websocket.user.UserConnection.receive_text',
        side_effect=['a', 'b', WebSocketDisconnect]
    )

    await shell_connection.listen_and_forward()

    send_text.assert_has_awaits([
        call(ShellIOSchema(
            connection_id=user_connection.id_,
            message="a"
        ).json()),
        call(ShellIOSchema(
            connection_id=user_connection.id_,
            message="b"
        ).json()),
    ])


@pytest.mark.asyncio
async def test_shell_connection_agent_connection_recovery(
    mocker,
    websocket_mock
):
    agent_connection = AgentConnection(websocket_mock, uuid.uuid4())
    user_connection = UserConnection(websocket_mock)
    await agent_connection.accept()
    await user_connection.accept()
    shell_connection = await ShellConnection.start(user_connection,
                                                   agent_connection)

    send_user_text = mocker.patch(
        'apollo.lib.websocket.user.UserConnection.send_text',
        wraps=user_connection.send_text
    )
    send_agent_text = mocker.patch(
        'apollo.lib.websocket.agent.AgentConnection.send_text',
        wraps=agent_connection.send_text,
        side_effect=[None, SendAfterConnectionClosure, None, None]
    )
    mocker.patch(
        'apollo.lib.websocket.user.UserConnection.receive_text',
        side_effect=['a', 'b', 'c', WebSocketDisconnect]
    )

    with patch(
        'apollo.lib.websocket.agent.AgentConnection.client_connected',
        new_callable=mocker.PropertyMock
    ) as connected_mock:
        connected_mock.side_effect = [False, False, True]
        await shell_connection.listen_and_forward()

        send_agent_text.assert_has_awaits([
            call(ShellIOSchema(
                connection_id=user_connection.id_,
                message="a"
            ).json()),
            call(ShellIOSchema(
                connection_id=user_connection.id_,
                message="b"
            ).json()),
            call(CommandSchema(
                connection_id=user_connection.id_,
                command=Command.NEW_CONNECTION
            ).json()),
            call(ShellIOSchema(
                connection_id=user_connection.id_,
                message="c"
            ).json()),
        ])

        send_user_text.assert_has_awaits([
            call(click.style(
                "\n\r\nConnection to agent lost. Reconnecting.. 0s",
                fg='red',
                bold=True
            )),
            call(click.style(
                "\n\r\nConnection to agent lost. Reconnecting.. 1s",
                fg='red',
                bold=True
            )),
            call(click.style("\n\r\nConnection recovered\n\r\n",
                             fg='green', bold=True)),
        ])
