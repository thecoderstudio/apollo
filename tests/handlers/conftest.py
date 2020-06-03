from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import close_all_sessions
from sqlalchemy_utils.functions import database_exists, create_database

from apollo import app
from apollo.lib.settings import settings
from apollo.models.user import User

@fixture
def test_client(monkeypatch):
    return TestClient(app)