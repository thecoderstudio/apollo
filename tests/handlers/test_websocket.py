import uuid
from tests.asserts import raisesHTTPForbidden

import pytest
from fastapi import APIRouter
from fastapi.websockets import WebSocket

import asyncio
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
async def test_web_socket_manager_add(test_client):
    websocket_manager = WebSocketManager()

    @app.websocket_route('/websocket_mock')
    async def mock(websocket: WebSocket):
        await websocket_manager.add_and_connect_websocket(websocket)

    with test_client.websocket_connect('/websocket_mock') as websocket:
        assert len(websocket_manager.connections) == 1

    with test_client.websocket_connect('/websocket_mock') as websocket:
        assert len(websocket_manager.connections) == 2

    await websocket_manager.close_and_remove_all_connections()


@pytest.mark.asyncio
async def test_web_socket_send_message(test_client):
    websocket_manager = WebSocketManager()

    @app.websocket_route('/websocket_connect')
    async def connect(websocket: WebSocket):
        websocket_manager.connections[uuid.uuid4()] = websocket
        await websocket.accept()

    with test_client.websocket_connect('/websocket_connect') as websocket:
        await websocket_manager.send_message(
            list(websocket_manager.connections)[0], "test_message")
        assert websocket.receive_json() == "test_message"
    await websocket_manager.close_and_remove_all_connections()
