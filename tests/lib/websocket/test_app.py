import json
from unittest.mock import call, patch

import pytest
from pydantic.json import pydantic_encoder
from starlette.websockets import WebSocketDisconnect

from apollo.lib.websocket.app import AppConnection
from apollo.lib.websocket.interest_type import (
    WebSocketObserverInterestType,
    InterestTypeFunctionHandler
)


def test_app_connection_random_id_on_construction(websocket_mock):
    a = AppConnection(websocket_mock)
    b = AppConnection(websocket_mock)
    assert a.id_ != b.id_


@pytest.mark.asyncio
async def test_app_connection_manager_get_connection(
    app_connection_manager,
    websocket_mock
):
    app_connection = AppConnection(websocket_mock)
    await app_connection_manager.accept_connection(app_connection)
    fetched_connection = app_connection_manager.get_connection(
        app_connection.id_)

    assert app_connection is fetched_connection


@pytest.mark.asyncio
async def test_app_connection_manager_connect(
    app_connection_manager,
    websocket_mock
):
    with patch(
        'apollo.lib.websocket.app.AppConnection.send_text'
    ) as send_text:
        with patch(
            'apollo.lib.websocket.app.AppConnection.receive_text',
            side_effect=['', WebSocketDisconnect]
        ):
            app_connection = await app_connection_manager.connect(
                websocket_mock,
                WebSocketObserverInterestType.AGENT_LISTING
            )

            send_text.assert_has_awaits([
                call('[]')
            ])

    assert isinstance(app_connection, AppConnection)
    with pytest.raises(KeyError):
        app_connection_manager.get_connection(app_connection.id_)


@pytest.mark.asyncio
async def test_app_connection_manager_message_interested_connections(
    app_connection_manager,
    mocker,
    websocket_mock
):
    interest_type = WebSocketObserverInterestType.AGENT_LISTING
    connection = AppConnection(websocket_mock)
    await app_connection_manager.accept_connection(connection)
    app_connection_manager._add_interested_connection(interest_type,
                                                      connection.id_)
    send_text = mocker.patch(
        'apollo.lib.websocket.app.AppConnection.send_text',
        wraps=connection.send_text
    )

    await app_connection_manager.message_interested_connections(interest_type)

    send_text.assert_awaited_with(
        json.dumps(
            InterestTypeFunctionHandler().run_corresponding_function(
                interest_type),
            default=pydantic_encoder
        )
    )
