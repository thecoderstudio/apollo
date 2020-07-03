import uuid

import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

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
    app_websocket_mock.send_json.assert_any_call(
        []
    )
    app_websocket_mock.close.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_to_connections(mocker, app_connection_manager,
                                           db_session):
    interest_type = WebSocketObserverInterestType.AGENT_LISTING

    app_websocket_mock = mocker.create_autospec(WebSocket)
    app_connection_manager.websocket_manager.open_app_connections = {
        interest_type: {
            uuid.uuid4(): app_websocket_mock
        }
    }

    await app_connection_manager.send_message_to_connections(
        interest_type
    )

    app_websocket_mock.send_json.assert_called_with(
        InterestTypeFunctionHandler().run_corresponding_function(
            interest_type
        )
    )
