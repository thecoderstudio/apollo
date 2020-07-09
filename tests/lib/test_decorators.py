import pytest

from apollo.lib.decorators import notify_websockets
from apollo.lib.websocket.interest_type import WebSocketObserverInterestType


@pytest.mark.asyncio
async def test_notify_websockets(mocker):
    mocked = mocker.patch('apollo.lib.websocket.app.AppConnectionManager.' +
                          'message_interested_connections')

    @notify_websockets(WebSocketObserverInterestType.AGENT_LISTING)
    def test():
        pass

    await test()
    mocked.assert_called_with(WebSocketObserverInterestType.AGENT_LISTING)
