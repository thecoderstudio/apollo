def test_shell(test_client):
    with test_client.websocket_connect('/ws') as websocket:
        assert websocket.receive_json() == "Connection accepted"
