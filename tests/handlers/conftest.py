from configparser import ConfigParser
from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, create_database

from apollo import app
from apollo.lib.settings import update_settings, settings
from apollo.models import init_sqlalchemy, get_connection_url, SessionLocal, get_session, Base, save
from apollo.models.user import User

from apollo import app

TestSession = sessionmaker(autocommit=False, autoflush=False)

def get_test_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@fixture
def test_client():
    app.dependency_overrides[get_session] = get_test_session
    return TestClient(app)

@fixture
def token(test_client):
    response = test_client.post(
        '/token',
        json={'username': 'johndoe', 'password': 'testing123'}
    )
    print(response)
    return response.json()['access_token']

@fixture(scope='session', autouse=True)
def database():
    engine = create_engine(get_connection_url(settings))
    TestSession.configure(bind=engine)
    Base.metadata.bind = engine
    
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all()
    
    user = User(
        username="johndoe",
        password_hash='$2b$12$q2ro/WdYipnZxYbPcjWgvuYB4aBI/JVYtPyroXs4SvvcS77p9Mwu2',
        password_salt='$2b$12$q2ro/WdYipnZxYbPcjWgvu'
    )
    # save(user)

    yield
    Base.metadata.drop_all() 