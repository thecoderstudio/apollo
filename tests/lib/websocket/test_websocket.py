from apollo.lib.websocket import WebSocketManager


def test_websocket_manager_is_singleton(mocker, websocket_manager):
    assert WebSocketManager() is websocket_manager
