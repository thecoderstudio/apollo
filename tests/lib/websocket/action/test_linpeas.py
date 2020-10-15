import uuid
from unittest.mock import call, patch

import pytest

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
    (True, 'test'),
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
        'test'
    )

    assert linpeas_manager.get_report(
        target_agent_id,
        ansi
    ) == expected_result


def test_manager_connect():
    pass
