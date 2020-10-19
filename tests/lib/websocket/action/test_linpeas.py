import uuid
from unittest.mock import call, patch

import pytest

from apollo.lib.schemas.message import (ServerCommand, ServerCommandSchema)
from apollo.lib.websocket.agent import AgentConnection
from apollo.lib.websocket.action.linpeas import (
    LinPEASConnection, REPORT_CACHE_TTL_IN_SECONDS, REPORT_CACHE_KEY_FORMAT)


@pytest.mark.asyncio
async def test_connection_send_text_report_building(
    websocket_mock,
    linpeas_manager
):
    connection = LinPEASConnection(
        linpeas_manager,
        uuid.uuid4(),
        websocket_mock
    )
    await connection.accept()
    with patch(
        'apollo.lib.websocket.user.UserConnection.send_text'
    ) as send_text:
        await connection.send_text('a')
        await connection.send_text('b')
        send_text.assert_has_awaits([call('a'), call('b')])
        assert connection.total_report == 'ab'


def test_connection_persist_report(
    websocket_mock,
    linpeas_manager,
    redis_session
):
    target_agent_id = uuid.uuid4()
    report = 'test'

    connection = LinPEASConnection(
        linpeas_manager,
        target_agent_id,
        websocket_mock
    )
    connection.total_report = report
    connection.persist_report()

    key = REPORT_CACHE_KEY_FORMAT.format(target_agent_id=target_agent_id)
    redis_session.get_from_cache(key) == report
    redis_session.get_ttl(key) == REPORT_CACHE_TTL_IN_SECONDS


@pytest.mark.parametrize('ansi, expected_result', [
    (True, '\x1b[1;31mtest\x1b[0m'),
    (False, 'test')
])
def test_manager_get_report(
    redis_session,
    linpeas_manager,
    ansi,
    expected_result
):
    target_agent_id = uuid.uuid4()
    redis_session.write_to_cache(
        REPORT_CACHE_KEY_FORMAT.format(
            target_agent_id=target_agent_id
        ),
        '\x1b[1;31mtest\x1b[0m'
    )

    assert linpeas_manager.get_report(
        target_agent_id,
        ansi
    ) == expected_result


def test_manager_get_report_not_found(linpeas_manager):
    assert linpeas_manager.get_report(uuid.uuid4()) is None


@pytest.mark.asyncio
async def test_linpeas_manager_process_server_command(
    agent_connection_manager,
    linpeas_manager,
    websocket_mock
):
    agent_connection = AgentConnection(websocket_mock, uuid.uuid4())
    await agent_connection_manager._accept_connection(agent_connection)

    linpeas_connection = LinPEASConnection(
        linpeas_manager,
        agent_connection.id_,
        websocket_mock
    )
    with patch(
        'apollo.lib.websocket.agent.AgentConnection.send_text',
        wraps=agent_connection.send_text
    ):
        await linpeas_manager._accept_connection(
            linpeas_connection)
        await linpeas_connection.send_text('a')
        await linpeas_connection.send_text('b')
        await linpeas_manager.process_server_command(
            ServerCommandSchema(
                connection_id=linpeas_connection.id_,
                command=ServerCommand.FINISHED
            )
        )

    assert linpeas_manager.get_report(agent_connection.id_) == 'ab'
    with pytest.raises(KeyError):
        linpeas_manager.get_connection(linpeas_connection.id_)
