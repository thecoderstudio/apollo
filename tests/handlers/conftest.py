from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, create_database

import apollo.models
from apollo import app
from apollo.lib.settings import settings
from apollo.models import get_connection_url, Base, save, get_session
from apollo.models.user import User

TestSession = sessionmaker(autocommit=False, autoflush=False)
engine = create_engine(get_connection_url(settings))
TestSession.configure(bind=engine)
Base.metadata.bind = engine

def get_test_session():
    session = TestSession()
    print("test session")
    try:
        yield session
    finally:
        print("closing session")
        session.close()

@fixture
def test_client(monkeypatch):
    return TestClient(app)

@fixture
def token(monkeypatch, test_client):
    monkeypatch.setattr('apollo.models.user.get_session', get_test_session)
    response = test_client.post(
        '/token',
        json={'username': 'johndoe', 'password': 'testing123'}
    )
    return response.json()['access_token']

@fixture(autouse=True)
def database(monkeypatch):
    monkeypatch.setattr('apollo.models.get_session', get_test_session)
    if not database_exists(engine.url):
        create_database(engine.url)
    
    Base.metadata.create_all()
    
    user = User(
        username="johndoe",
        password_hash='$2b$12$q2ro/WdYipnZxYbPcjWgvuYB4aBI/JVYtPyroXs4SvvcS77p9Mwu2',
        password_salt='$2b$12$q2ro/WdYipnZxYbPcjWgvu'
    )
    save(user)

    yield
    engine.dispose()
    Base.metadata.drop_all(engine)
