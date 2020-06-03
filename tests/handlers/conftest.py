from fastapi.testclient import TestClient
from pytest import fixture

from apollo import app

@fixture
def test_client():
    return TestClient(app)