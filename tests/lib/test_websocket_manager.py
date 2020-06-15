import json
import uuid

import pytest
from fastapi.websockets import WebSocket

from apollo import app
from apollo.lib.websocket_manager import WebSocketManager
from apollo.models.agent import Agent


@pytest.mark.asyncio
async def test_websocket_manager_add(test_client, db_session):
    websocket_manager = WebSocketManager()

    agent = Agent(name='agent1')
    agent_2 = Agent(name='agent2')
    db_session.add(agent)
    db_session.add(agent_2)
    db_session.flush()
    ids = [agent.id, agent_2.id]
    db_session.commit()

    @app.websocket_route('/websocket_mock')
    async def mock(websocket: WebSocket):
        await websocket_manager.add_and_connect_websocket(ids.pop(0),
                                                          websocket)

    test_client.websocket_connect('/websocket_mock')
    assert len(websocket_manager.connections) == 1

    # test_client.websocket_connect('/websocket_mock')
    # assert len(websocket_manager.connections) == 2

    await websocket_manager.close_and_remove_all_connections()


# @pytest.mark.asyncio
# async def test_websocket_manager_send_message(test_client):
#     websocket_manager = WebSocketManager()
#     add_websocket_connect_route(app)
#     with test_client.websocket_connect('/websocket_connect') as websocket:
#         await websocket_manager.send_message(
#             list(websocket_manager.connections)[0], 'test_message')
#         assert websocket.receive_json()['message'] == 'test_message'
#     await websocket_manager.close_and_remove_all_connections()


# @pytest.mark.asyncio
# async def test_wesocket_manager_close_and_remove_connections(test_client):
#     websocket_manager = WebSocketManager()
#     add_websocket_connect_route(app)
#     test_client.websocket_connect('/websocket_connect')
#     assert len(websocket_manager.connections) == 1
#     await websocket_manager.close_and_remove_all_connections()
#     assert len(websocket_manager.connections) == 0


# @pytest.mark.asyncio
# async def test_websocket_manager_close_runetime_error(test_client):
#     websocket_manager = WebSocketManager()
#     add_websocket_connect_route(app)
#     test_client.websocket_connect('/websocket_connect')
#     await list(websocket_manager.connections.values())[0].close()
#     await websocket_manager.close_and_remove_all_connections()


# @pytest.mark.asyncio
# async def test_wait_for_response(test_client):
#     websocket_manager = WebSocketManager()
#     add_websocket_connect_route(app)
#     with test_client.websocket_connect('/websocket_connect') as websocket:
#         message_id = uuid.uuid4()
#         await list(websocket_manager.connections.values())[0].send_json({
#             'message_id': str(message_id),
#             'message': 'message'
#         })
#         response = await websocket_manager.wait_for_response(message_id)
#         assert response['message_id'] == message_id


# def add_websocket_connect_route(app):
#     @ app.websocket_route('/websocket_connect')
#     async def connect(websocket: WebSocket):
#         WebSocketManager().connections[uuid.uuid4()] = websocket
#         await websocket.accept()
