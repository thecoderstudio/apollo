from tests.asserts import raisesHTTPForbidden


def test_shell(test_client, authenticated_agent_headers):
    with test_client.websocket_connect(
        '/ws', headers=authenticated_agent_headers
    ) as websocket:
        assert websocket.receive_json() == "Connection accepted"


def test_shell_unauthenticated(test_client):
    with raisesHTTPForbidden:
        test_client.websocket_connect('/ws')
