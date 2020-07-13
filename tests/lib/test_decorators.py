import pytest

from apollo.lib.decorators import notify_websockets
from apollo.lib.websocket.interest_type import WebSocketObserverInterestType
from tests.lib.websocket import assert_interested_connections_messaged


@pytest.mark.asyncio
@assert_interested_connections_messaged(
    WebSocketObserverInterestType.AGENT_LISTING)
async def test_notify_websockets(mocker):
    @notify_websockets(WebSocketObserverInterestType.AGENT_LISTING)
    def test():
        pass

    await test()
