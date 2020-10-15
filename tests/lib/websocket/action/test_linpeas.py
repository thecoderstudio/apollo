import uuid

import pytest

from apollo.lib.websocket.action.linpeas import LinPEASConnection


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
    await connection.send_text('a')
    await connection.send_text('b')
    assert connection.total_report == 'ab'


def test_connection_persist_report():
    pass


@pytest.mark.parametrize('ansi', [True, False])
def test_manager_get_report(ansi):
    pass


def test_manager_connect():
    pass
