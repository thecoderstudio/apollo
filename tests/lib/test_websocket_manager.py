import asyncio
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

    with test_client.websocket_connect('/websocket_mock'):
        assert len(websocket_manager.connections) == 1

    with test_client.websocket_connect('/websocket_mock'):
        assert len(websocket_manager.connections) == 2

    await websocket_manager.close_and_remove_all_connections()


@pytest.mark.asyncio
async def test_wesocket_manager_close_and_remove_connections(test_client):
    websocket_manager = WebSocketManager()
    add_websocket_connect_route(app)
    with test_client.websocket_connect('/websocket_connect'):
        assert len(websocket_manager.connections) == 1

        await websocket_manager.close_and_remove_all_connections()
        assert len(websocket_manager.connections) == 0


@pytest.mark.asyncio
async def test_wesocket_manager_close_and_remove_connection(test_client):
    websocket_manager = WebSocketManager()
    add_websocket_connect_route(app)
    with test_client.websocket_connect('/websocket_connect'):
        assert len(websocket_manager.connections) == 1

        await websocket_manager.close_and_remove_connection(
            list(websocket_manager.connections.keys())[0]
        )
        assert len(websocket_manager.connections) == 0


@pytest.mark.asyncio
async def test_websocket_manager_close_runetime_error(test_client):
    websocket_manager = WebSocketManager()
    add_websocket_connect_route(app)
    with test_client.websocket_connect('/websocket_connect'):
        await list(websocket_manager.connections.values())[0].close()
        await websocket_manager.close_and_remove_all_connections()


@pytest.mark.asyncio
async def test_websocket_manager_close_runetime_error_unexpected(test_client):

    class WebSocketMock:
        @staticmethod
        async def send_json(message):
            return message

        @staticmethod
        async def close():
            raise RuntimeError()

        @staticmethod
        async def accept():
            asyncio.sleep(1)
            return "accepted"

    class WebSocketManagerMock(WebSocketManager):

        def __init__(self):
            self.connections: Dict[uuid.UUID, WebSocketMock] = {}

    websocket_manager = WebSocketManagerMock()

    with pytest.raises(RuntimeError):
        id = uuid.uuid4()
        websocket = WebSocketMock()
        websocket_manager.connections[id] = websocket
        await websocket_manager.close_and_remove_connection(id)

        await websocket_manager.close_and_remove_all_connections()


@pytest.mark.asyncio
async def test_send_message_and_wait_for_response_catch_disconnect(
        test_client):
    websocket_manager = WebSocketManager()

    @app.websocket_route('/send_message_disconnect')
    async def send_message(websocket: WebSocket):
        response = await setup_websocket_send_message_route(websocket)
        assert response is None

    with test_client.websocket_connect('/send_message_disconnect'):
        pass

    await websocket_manager.close_and_remove_all_connections()


@pytest.mark.asyncio
async def test_send_message_and_wait_for_response_sucess_key_error_catch(
        test_client):
    websocket_manager = WebSocketManager()

    @app.websocket_route('/send_message')
    async def send_message(websocket: WebSocket):
        response = await setup_websocket_send_message_route(websocket)
        assert response['message'] == 'message'

    with test_client.websocket_connect(
            '/send_message') as target_websocket:
        response = target_websocket.receive_json()
        target_websocket.send_json({
            'message': 'message'
        })
        target_websocket.send_json({
            'message_id': str(response['message_id']),
            'message': 'message'
        })

    await websocket_manager.close_and_remove_all_connections()


@pytest.mark.asyncio
async def test_send_message_and_wait_for_response_sucess(test_client):
    websocket_manager = WebSocketManager()

    @app.websocket_route('/send_message')
    async def send_message(websocket: WebSocket):
        response = await setup_websocket_send_message_route(websocket)
        assert response['message'] == 'message'

    with test_client.websocket_connect(
            '/send_message') as target_websocket:
        response = target_websocket.receive_json()
        target_websocket.send_json({
            'message_id': str(response['message_id']),
            'message': 'message'
        })

    await websocket_manager.close_and_remove_all_connections()


def add_websocket_connect_route(app):
    @app.websocket_route('/websocket_connect')
    async def connect(websocket: WebSocket):
        await add_websocket_to_manager_and_accept(websocket)


async def setup_websocket_send_message_route(websocket):
    await add_websocket_to_manager_and_accept(websocket)
    websocket_manager = WebSocketManager()
    response = await websocket_manager.send_message_and_wait_for_response(
        target_websocket_id=list(
            websocket_manager.connections.keys())[0],
        message={'message': 'message'}
    )
    return response


async def add_websocket_to_manager_and_accept(websocket):
    WebSocketManager().connections[uuid.uuid4()] = websocket
    await websocket.accept()
