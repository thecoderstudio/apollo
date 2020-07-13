import uuid
from unittest.mock import patch

import pytest
from starlette.websockets import WebSocketDisconnect, WebSocketState

from apollo.lib.exceptions.websocket import SendAfterConnectionClosure
from apollo.lib.websocket.connection import Connection


@pytest.mark.parametrize("state, expect_connected", [
    (WebSocketState.DISCONNECTED, False),
    (WebSocketState.CONNECTING, False),
    (WebSocketState.CONNECTED, True)
])
def test_connection_client_connected(websocket_mock, state, expect_connected):
    connection = Connection(websocket_mock, uuid.uuid4())
    connection.client_state = state
    assert connection.client_connected is expect_connected


def test_connection_hash(websocket_mock):
    id_ = uuid.uuid4()
    a = Connection(websocket_mock, id_)
    b = Connection(websocket_mock, id_)

    assert a.__hash__() == b.__hash__()


def test_connection_eq(websocket_mock):
    id_ = uuid.uuid4()
    a = Connection(websocket_mock, id_)
    b = Connection(websocket_mock, id_)

    assert a == b


def test_connection_connect(websocket_mock):
    websocket_mock.client_state = WebSocketState.DISCONNECTED
    connection = Connection(websocket_mock, uuid.uuid4())
    assert not connection.client_connected

    websocket_mock.client_state = WebSocketState.CONNECTED
    connection.connect(websocket_mock)

    assert connection.client_connected


@pytest.mark.asyncio
async def test_connection_listen(websocket_mock):
    connection = Connection(websocket_mock, uuid.uuid4())
    with patch('apollo.lib.websocket.connection.Connection._receive_message',
               side_effect=['a', 'b', WebSocketDisconnect]):
        result = [message async for message in connection.listen()]

    assert result == ['a', 'b']
    assert connection.application_state is WebSocketState.DISCONNECTED


@pytest.mark.asyncio
async def test_connection_send(websocket_mock):
    connection = Connection(websocket_mock, uuid.uuid4())
    await connection.accept()
    message = {
        'type': 'websocket.send',
        'text': 'test'
    }

    await connection.send(message)
    websocket_mock._send.assert_awaited_with(message)


@pytest.mark.asyncio
async def test_connection_send_after_closure(websocket_mock):
    connection = Connection(websocket_mock, uuid.uuid4())
    await connection.accept()
    await connection.close()

    with pytest.raises(SendAfterConnectionClosure):
        await connection.send({
            'type': 'websocket.send',
            'text': 'test'
        })


@pytest.mark.asyncio
async def test_connection_send_unexpected_runtime_error(websocket_mock):
    connection = Connection(websocket_mock, uuid.uuid4())
    await connection.accept()
    await connection.close()

    with patch('fastapi.WebSocket.send', side_effect=RuntimeError):
        with pytest.raises(RuntimeError) as e:
            await connection.send({
                'type': 'websocket.send',
                'text': 'test'
            })
            assert not isinstance(e, SendAfterConnectionClosure)


@pytest.mark.asyncio
async def test_connection_close(websocket_mock):
    connection = Connection(websocket_mock, uuid.uuid4())
    await connection.accept()
    await connection.close()
    assert connection.application_state is WebSocketState.DISCONNECTED


@pytest.mark.asyncio
async def test_connection_close_after_closure(websocket_mock):
    connection = Connection(websocket_mock, uuid.uuid4())
    await connection.accept()
    await connection.close()

    await connection.close()


@pytest.mark.asyncio
async def test_connection_close_unexpected_runtime_error(websocket_mock):
    connection = Connection(websocket_mock, uuid.uuid4())
    await connection.accept()
    await connection.close()

    with patch('fastapi.WebSocket.close', side_effect=RuntimeError):
        with pytest.raises(RuntimeError) as e:
            await connection.close()
            assert not isinstance(e, SendAfterConnectionClosure)
