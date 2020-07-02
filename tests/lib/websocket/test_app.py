import uuid

import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from apollo.lib.websocket.interest_type import WebSocketObserverInterestType
from apollo.models.agent import Agent


def test_websocket_observer_interest_list_all_agents(db_session):
    agent = Agent(name='test')
    db_session.add(agent)
    db_session.commit()

    data = WebSocketObserverInterestType._list_all_agents()
    assert len(data) == 1
    assert data[0]['connection_state'] == 'disconnected'


@pytest.mark.asyncio
async def test_connect_and_send(mocker, app_connection_manager, db_session):
    app_websocket_mock = mocker.create_autospec(WebSocket)
    app_websocket_mock.receive_text.side_effect = WebSocketDisconnect

    await app_connection_manager.connect_and_send(
        app_websocket_mock,
        WebSocketObserverInterestType.AGENT_LISTING
    )

    app_websocket_mock.receive_text.assert_called_once()
    app_websocket_mock.send_json.assert_called()
    app_websocket_mock.close.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_to_connections(mocker, app_connection_manager,
                                           db_session):
    app_websocket_mock = mocker.create_autospec(WebSocket)
    app_connection_manager.websocket_manager.open_app_connections = {
        WebSocketObserverInterestType.AGENT_LISTING: {
            uuid.uuid4(): app_websocket_mock
        }
    }

    await app_connection_manager.send_message_to_connections(
        WebSocketObserverInterestType.AGENT_LISTING
    )

    app_websocket_mock.send_json.assert_called_with(
        WebSocketObserverInterestType.AGENT_LISTING()
    )
