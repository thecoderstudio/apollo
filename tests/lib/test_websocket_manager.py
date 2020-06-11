import pytest
from fastapi import APIRouter

from apollo.lib.websocket_manager import WebSocketManager


# def test_web_socket_manager_add(test_client):
#     # from fastapi.testclient import TestClient
#     # from apollo import app
#     print(test_client)

# with test_client.websocket_connect('/') as websocket:
#     WebSocketManager().add_and_connect_websocket(websocket)
#     assert len(WebSocketManager().connections) == 1
#     WebSocketManager().add_and_connect_websocket(websocket)
#     assert len(WebSocketManager().connections) == 2
