import pytest
from unittest.mock import patch, AsyncMock

from apollo.lib.decorators import notify_websockets
from apollo.lib.websocket.app import WebSocketObserverInterestTypes


@pytest.mark.asyncio
async def test_notify_websockets(mocker):

    mocked = mocker.patch('apollo.lib.websocket.app.AppConnectionManager',
                          autospec=True)
    mocked.send_message_to_connections.side_effect = "test"

    @notify_websockets(WebSocketObserverInterestTypes.AGENT_LISTING)
    def test():
        print("function")

    await test()
    mocked.assert_called()
