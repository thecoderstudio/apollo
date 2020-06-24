import uuid

import pytest
from fastapi import WebSocket

from apollo.lib.websocket import ConnectionManager


@pytest.mark.asyncio
async def test_connect_agent(mocker, websocket_manager):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)
    mock_agent_id = uuid.uuid4()

    await websocket_manager.connect_agent(mock_agent_id, websocket_mock)

    assert (websocket_manager.open_agent_connections[mock_agent_id] is
            websocket_mock)
    websocket_mock.accept.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("closed_connection", [True, False])
async def test_close_agent_connection(mocker, websocket_manager,
                                      closed_connection):
    manager = websocket_manager

    mock_agent_id = uuid.uuid4()
    agent_websocket_mock = mocker.create_autospec(WebSocket)
    await manager.connect_agent(mock_agent_id, agent_websocket_mock)

    if closed_connection:
        agent_websocket_mock.send_json.side_effect = RuntimeError(
            'Cannot call "send" once a close message has been sent.'
        )

    await manager.close_agent_connection(mock_agent_id)

    agent_websocket_mock.send_json.assert_awaited_once_with(
        "Closing connection")

    if not closed_connection:
        agent_websocket_mock.close.assert_awaited_once()

    with pytest.raises(KeyError):
        assert manager.get_agent_connection(mock_agent_id)


@pytest.mark.asyncio
async def test_connect_user(mocker, websocket_manager):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)

    connection_id = await websocket_manager.connect_user(websocket_mock)

    assert (websocket_manager.open_user_connections[connection_id] is
            websocket_mock)
    websocket_mock.accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_agent_connection(mocker, websocket_manager):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)
    mock_agent_id = uuid.uuid4()
    await websocket_manager.connect_agent(mock_agent_id, websocket_mock)

    connection = websocket_manager.get_agent_connection(mock_agent_id)

    assert connection is websocket_mock


@pytest.mark.asyncio
async def test_get_agent_connection_not_found(websocket_manager):
    with pytest.raises(KeyError):
        await websocket_manager.get_agent_connection(uuid.uuid4())


@pytest.mark.asyncio
async def test_get_user_connection(mocker, websocket_manager):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)
    connection_id = await websocket_manager.connect_user(websocket_mock)

    connection = websocket_manager.get_user_connection(connection_id)

    assert connection is websocket_mock


@pytest.mark.asyncio
async def test_get_user_connection_not_found(websocket_manager):
    with pytest.raises(KeyError):
        await websocket_manager.get_user_connection(uuid.uuid4())


@pytest.mark.asyncio
async def test_message_agent(mocker, websocket_manager):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)
    mock_agent_id = uuid.uuid4()
    sender_id = uuid.uuid4()
    await websocket_manager.connect_agent(mock_agent_id, websocket_mock)

    await websocket_manager.message_agent(sender_id, mock_agent_id, 'test')

    websocket_mock.send_json.assert_awaited_once_with({
        'connection_id': str(sender_id),
        'message': 'test'
    })


@pytest.mark.asyncio
async def test_message_agent_not_found(websocket_manager):
    with pytest.raises(KeyError):
        await websocket_manager.message_agent(uuid.uuid4(), uuid.uuid4(),
                                              'test')


@pytest.mark.asyncio
async def test_message_user(mocker, websocket_manager):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)
    connection_id = await websocket_manager.connect_user(websocket_mock)

    await websocket_manager.message_user(connection_id, 'test')

    websocket_mock.send_text.assert_awaited_once_with('test')


@pytest.mark.asyncio
async def test_message_user_not_found(websocket_manager):
    with pytest.raises(KeyError):
        await websocket_manager.message_user(uuid.uuid4(), 'test')


def test_connection_manager_get_connection(websocket_manager):
    manager = ConnectionManager()
    manager.websocket_manager = websocket_manager

    with pytest.raises(NotImplementedError):
        manager.get_connection(uuid.uuid4())
