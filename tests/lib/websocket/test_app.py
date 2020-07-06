import uuid

import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
from unittest.mock import patch

from apollo.lib.websocket.interest_type import (
    WebSocketObserverInterestType,
    InterestTypeFunctionHandler
)


@pytest.mark.asyncio
async def test_connect_and_send(mocker, app_connection_manager, db_session):
    app_websocket_mock = mocker.create_autospec(WebSocket)
    app_websocket_mock.receive_text.side_effect = WebSocketDisconnect

    await app_connection_manager.connect_and_send(
        app_websocket_mock,
        WebSocketObserverInterestType.AGENT_LISTING
    )

    app_websocket_mock.receive_text.assert_called_once()
    app_websocket_mock.send_json.assert_any_call([])
    app_websocket_mock.close.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_to_connections(mocker, app_connection_manager,
                                           db_session):
    interest_type = WebSocketObserverInterestType.AGENT_LISTING

    app_websocket_mock = mocker.create_autospec(WebSocket)
    app_connection_manager._add_interested_connection(interest_type,
                                                      uuid.uuid4())

    await app_connection_manager.send_message_to_connections(interest_type)

    app_websocket_mock.send_json.assert_called_with(
        InterestTypeFunctionHandler().run_corresponding_function(interest_type)
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("closed_connection", [True, False])
async def test_close_connection(mocker, app_connection_manager,
                                closed_connection):
    manager = app_connection_manager

    websocket_mock = mocker.create_autospec(WebSocket)
    connection_id = await manager.websocket_manager.connect_app(
        websocket_mock)

    if closed_connection:
        websocket_mock.send_json.side_effect = RuntimeError(
            'Cannot call "send" once a close message has been sent.'
        )

    await manager.close_connection(connection_id)

    websocket_mock.send_json.assert_awaited_once_with("Closing connection")

    if not closed_connection:
        websocket_mock.close.assert_awaited_once()

    with pytest.raises(KeyError):
        assert manager.get_connection(connection_id)


@pytest.mark.asyncio
@pytest.mark.parametrize("closed_connection", [True, False])
async def test_close_connect_unexpected_runtime_error(
        mocker, app_connection_manager, closed_connection
):
    websocket_mock = mocker.create_autospec(WebSocket)
    connection_id = await app_connection_manager.websocket_manager.connect_app(
        websocket_mock)

    websocket_mock.send_json.side_effect = RuntimeError('Test unexpected')

    with pytest.raises(RuntimeError, match='Test unexpected'):
        await app_connection_manager.close_connection(connection_id)

    assert app_connection_manager.get_connection(
        connection_id) is websocket_mock


@pytest.mark.asyncio
async def test_get_connection(mocker, app_connection_manager):
    websocket_mock = mocker.create_autospec(WebSocket)
    connection_id = await (
        app_connection_manager.websocket_manager.connect_app(websocket_mock)
    )

    assert (app_connection_manager.get_connection(connection_id) is
            websocket_mock)


@pytest.mark.asyncio
async def test_remove_connection_value_error(app_connection_manager):
    with patch(
        'apollo.lib.websocket.app.AppConnectionManager.close_connection'
    ):
        app_connection_manager.interested_connections[
            WebSocketObserverInterestType.AGENT_LISTING
        ] = [uuid.uuid4()]

        try:
            await app_connection_manager._close_and_remove_connection(
                uuid.uuid4())
        except KeyError:
            pytest.fail("Method did raise KeyError")


def test_get_connection_not_found(app_connection_manager):
    with pytest.raises(KeyError):
        app_connection_manager.get_connection(uuid.uuid4())
