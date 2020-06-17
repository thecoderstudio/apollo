import uuid
from tests.asserts import raisesHTTPForbidden

import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketState

from apollo import app
from apollo.lib.websocket_manager import WebSocketManager


@pytest.mark.asyncio
async def test_shell(test_client, authenticated_agent_headers):
    with test_client.websocket_connect(
        '/ws', headers=authenticated_agent_headers
    ) as websocket:
        assert websocket.receive_json() == "Connection accepted"

    websocket_manager = WebSocketManager()
    await websocket_manager.close_and_remove_all_connections()


def test_shell_unauthenticated(test_client):
    with raisesHTTPForbidden:
        test_client.websocket_connect('/ws')


@pytest.mark.asyncio
async def test_close_websocket_connect(test_client):
    websocket_id = uuid.uuid4()
    websocket_manager = WebSocketManager()

    @app.websocket_route('/websocket_connect')
    async def connect(websocket: WebSocket):
        websocket_manager.connections[websocket_id] = websocket
        await websocket.accept()

    with test_client.websocket_connect('/websocket_connect'):
        test_client.websocket_connect(f'ws/{websocket_id}')

        assert (websocket_manager.connections[websocket_id].client_state
                == WebSocketState.DISCONNECTED)
