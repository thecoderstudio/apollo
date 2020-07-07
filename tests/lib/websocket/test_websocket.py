import uuid
from unittest.mock import patch

import pytest
from fastapi import WebSocket
from websockets.exceptions import ConnectionClosed

from apollo.lib.schemas.message import ShellIOSchema
from apollo.lib.websocket import ConnectionManager
from apollo.lib.websocket.interest_type import WebSocketObserverInterestType


@pytest.mark.asyncio
async def test_connect_agent(mocker, websocket_manager):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)
    mock_agent_id = uuid.uuid4()

    with patch('apollo.lib.websocket.app.AppConnectionManager.'
               + 'send_message_to_connections') as patched_function:
        await websocket_manager.connect_agent(mock_agent_id, websocket_mock)
        assert (websocket_manager.open_agent_connections[mock_agent_id] is
                websocket_mock)

        patched_function.assert_called_with(
            WebSocketObserverInterestType.AGENT_LISTING
        )

    websocket_mock.accept.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("side_effect", [
    None,
    RuntimeError('Cannot call "send" once a close message has been sent'),
    ConnectionClosed(code=1000, reason="connection closed")
])
async def test_close_agent_connection(mocker, websocket_manager,
                                      side_effect):
    manager = websocket_manager

    mock_agent_id = uuid.uuid4()
    agent_websocket_mock = mocker.create_autospec(WebSocket)
    await manager.connect_agent(mock_agent_id, agent_websocket_mock)

    if side_effect:
        agent_websocket_mock.send_json.side_effect = side_effect

    with patch('apollo.lib.websocket.app.AppConnectionManager.'
               + 'send_message_to_connections') as patched_function:
        await manager.close_agent_connection(mock_agent_id)

        agent_websocket_mock.send_json.assert_awaited_once_with(
            "Closing connection")

        if not side_effect:
            agent_websocket_mock.close.assert_awaited_once()
            patched_function.assert_called_with(
                WebSocketObserverInterestType.AGENT_LISTING
            )

        with pytest.raises(KeyError):
            assert manager.get_agent_connection(mock_agent_id)


@pytest.mark.asyncio
async def test_close_agent_connection_unexpected_runtime_error(
    mocker, websocket_manager
):
    manager = websocket_manager
    mock_agent_id = uuid.uuid4()
    agent_websocket_mock = mocker.create_autospec(WebSocket)
    await manager.connect_agent(mock_agent_id, agent_websocket_mock)

    agent_websocket_mock.send_json.side_effect = RuntimeError(
        "Test unexpected"
    )

    with pytest.raises(RuntimeError, match="Test unexpected"):
        await manager.close_agent_connection(mock_agent_id)

    assert manager.get_agent_connection(mock_agent_id) is agent_websocket_mock


@pytest.mark.asyncio
@pytest.mark.parametrize("side_effect", [
    None,
    RuntimeError('Cannot call "send" once a close message has been sent'),
    ConnectionClosed(code=1000, reason="connection closed")
])
async def test_close_user_connection(mocker, websocket_manager,
                                     side_effect):
    manager = websocket_manager

    user_websocket_mock = mocker.create_autospec(WebSocket)
    connection_id = await manager.connect_user(user_websocket_mock)

    if side_effect:
        user_websocket_mock.send_json.side_effect = side_effect

    await manager.close_user_connection(connection_id)

    user_websocket_mock.send_json.assert_awaited_once_with(
        "Closing connection")

    if not side_effect:
        user_websocket_mock.close.assert_awaited_once()

    with pytest.raises(KeyError):
        assert manager.get_user_connection(connection_id)


@pytest.mark.asyncio
async def test_close_user_connection_unexpected_runtime_error(
    mocker, websocket_manager
):
    manager = websocket_manager
    user_websocket_mock = mocker.create_autospec(WebSocket)
    connection_id = await manager.connect_user(user_websocket_mock)

    user_websocket_mock.send_json.side_effect = RuntimeError(
        "Test unexpected"
    )

    with pytest.raises(RuntimeError, match="Test unexpected"):
        await manager.close_user_connection(connection_id)

    assert manager.get_user_connection(connection_id) is user_websocket_mock


@pytest.mark.asyncio
@pytest.mark.parametrize("side_effect", [
    None,
    RuntimeError('Cannot call "send" once a close message has been sent'),
    ConnectionClosed(code=1000, reason="connection closed")
])
async def test_close_app_connection(mocker, websocket_manager,
                                    side_effect, db_session):
    manager = websocket_manager

    app_websocket_mock = mocker.create_autospec(WebSocket)
    connection_id = await manager.connect_app(
        app_websocket_mock,
    )

    if side_effect:
        app_websocket_mock.send_json.side_effect = side_effect

    await manager.close_app_connection(
        connection_id
    )

    app_websocket_mock.send_json.assert_awaited_once_with(
        "Closing connection")

    if not side_effect:
        app_websocket_mock.close.assert_awaited_once()

    with pytest.raises(KeyError):
        assert manager.get_app_connection(
            connection_id
        )


@pytest.mark.asyncio
async def test_connect_app(mocker, websocket_manager, db_session):
    websocket_mock = mocker.patch('fastapi.WebSocket', autospec=True)

    connection_id = await websocket_manager.connect_app(websocket_mock)

    assert (websocket_manager.open_app_connections[
            connection_id] is websocket_mock)

    websocket_mock.accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_user(mocker, websocket_manager, db_session):
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
    message = ShellIOSchema(
        connection_id=uuid.uuid4(),
        message='test'
    )

    await websocket_manager.connect_agent(mock_agent_id, websocket_mock)
    await websocket_manager.message_agent(mock_agent_id, message)

    websocket_mock.send_text.assert_awaited_once_with(message.json())


@pytest.mark.asyncio
async def test_message_agent_not_found(websocket_manager):
    with pytest.raises(KeyError):
        await websocket_manager.message_agent(
            uuid.uuid4(),
            ShellIOSchema(
                connection_id=uuid.uuid4(),
                message='test'
            )
        )


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


@pytest.mark.asyncio
async def test_connection_manager_close_connection(websocket_manager):
    manager = ConnectionManager()
    manager.websocket_manager = websocket_manager

    with pytest.raises(NotImplementedError):
        await manager.close_connection(uuid.uuid4())
