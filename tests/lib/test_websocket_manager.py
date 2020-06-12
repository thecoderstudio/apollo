import uuid

import pytest
from fastapi import APIRouter
from fastapi.websockets import WebSocket

from apollo import app
from apollo.lib.websocket_manager import WebSocketManager


@pytest.mark.asyncio
async def test_websocket_manager_add(test_client):
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
async def test_websocket_manager_send_message(test_client):
    websocket_manager = WebSocketManager()
    add_websocket_connect_route(app)
    with test_client.websocket_connect('/websocket_connect') as websocket:
        await websocket_manager.send_message(
            list(websocket_manager.connections)[0], "test_message")
        assert websocket.receive_json() == "test_message"
    await websocket_manager.close_and_remove_all_connections()


@pytest.mark.asyncio
async def test_wesocket_manager_close_and_remove_connections(test_client):
    websocket_manager = WebSocketManager()
    add_websocket_connect_route(app)
    test_client.websocket_connect('/websocket_connect')
    assert len(websocket_manager.connections) == 1
    await websocket_manager.close_and_remove_all_connections()
    assert len(websocket_manager.connections) == 0


@pytest.mark.asyncio
async def test_websocket_manager_close_runetime_error(test_client):
    websocket_manager = WebSocketManager()
    add_websocket_connect_route(app)
    test_client.websocket_connect('/websocket_connect')
    await list(websocket_manager.connections.values())[0].close()
    await websocket_manager.close_and_remove_all_connections()


def add_websocket_connect_route(app):
    @app.websocket_route('/websocket_connect')
    async def connect(websocket: WebSocket):
        WebSocketManager().connections[uuid.uuid4()] = websocket
        await websocket.accept()

