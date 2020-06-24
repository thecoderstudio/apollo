import uuid

import pytest

from apollo.lib.websocket import ConnectionManager, WebSocketManager


@pytest.mark.asyncio
async def test_connect_agent(mocker):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)
    mock_agent_id = uuid.uuid4()
    manager = WebSocketManager()

    await manager.connect_agent(mock_agent_id, websocket_mock)

    assert manager.open_agent_connections[mock_agent_id] is websocket_mock
    websocket_mock.accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_user(mocker):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)
    manager = WebSocketManager()

    connection_id = await manager.connect_user(websocket_mock)

    assert manager.open_user_connections[connection_id] is websocket_mock
    websocket_mock.accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_agent_connection(mocker):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)
    mock_agent_id = uuid.uuid4()
    manager = WebSocketManager()
    await manager.connect_agent(mock_agent_id, websocket_mock)

    connection = manager.get_agent_connection(mock_agent_id)

    assert connection is websocket_mock


@pytest.mark.asyncio
async def test_get_agent_connection_not_found():
    manager = WebSocketManager()

    with pytest.raises(KeyError):
        await manager.get_agent_connection(uuid.uuid4())


@pytest.mark.asyncio
async def test_get_user_connection(mocker):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)
    manager = WebSocketManager()
    connection_id = await manager.connect_user(websocket_mock)

    connection = manager.get_user_connection(connection_id)

    assert connection is websocket_mock


@pytest.mark.asyncio
async def test_get_user_connection_not_found():
    manager = WebSocketManager()

    with pytest.raises(KeyError):
        await manager.get_user_connection(uuid.uuid4())


@pytest.mark.asyncio
async def test_message_agent(mocker):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)
    mock_agent_id = uuid.uuid4()
    sender_id = uuid.uuid4()
    manager = WebSocketManager()
    await manager.connect_agent(mock_agent_id, websocket_mock)

    await manager.message_agent(sender_id, mock_agent_id, 'test')

    websocket_mock.send_json.assert_awaited_once_with({
        'connection_id': str(sender_id),
        'message': 'test'
    })


@pytest.mark.asyncio
async def test_message_agent_not_found():
    manager = WebSocketManager()

    with pytest.raises(KeyError):
        await manager.message_agent(uuid.uuid4(), uuid.uuid4(), 'test')


@pytest.mark.asyncio
async def test_message_user(mocker):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)
    manager = WebSocketManager()
    connection_id = await manager.connect_user(websocket_mock)

    await manager.message_user(connection_id, 'test')

    websocket_mock.send_text.assert_awaited_once_with('test')


@pytest.mark.asyncio
async def test_message_user_not_found():
    manager = WebSocketManager()

    with pytest.raises(KeyError):
        await manager.message_user(uuid.uuid4(), 'test')


def test_connection_manager_get_connection():
    with pytest.raises(NotImplementedError):
        ConnectionManager().get_connection(uuid.uuid4())
