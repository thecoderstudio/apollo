import pytest

from apollo.lib.decorators import notify_websockets
from apollo.lib.websocket.interest_type import WebSocketObserverInterestTypes


@pytest.mark.asyncio
async def test_notify_websockets(mocker):

    mocked = mocker.patch('apollo.lib.websocket.app.AppConnectionManager',
                          autospec=True)

    @notify_websockets(WebSocketObserverInterestTypes.AGENT_LISTING)
    def test():
        pass

    await test()
    mocked.assert_called()
