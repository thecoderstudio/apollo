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

# @fixture(scope='session', autouse=True)
# def database():
#     if not database_exists(engine.url):
#         create_database(engine.url)

#     Base.metadata.create_all()

#     user = User(
#         username="johndoe",
#         password_hash='$2b$12$q2ro/WdYipnZxYbPcjWgvuYB4aBI/JVYtPyroXs4SvvcS77p9Mwu2',
#         password_salt='$2b$12$q2ro/WdYipnZxYbPcjWgvu'
#     )
#     save(user)

#     yield
#     close_all_sessions()
#     Base.metadata.drop_all(engine)
