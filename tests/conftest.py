import contextlib
from configparser import ConfigParser

from fastapi.testclient import TestClient
from pytest import fixture

from apollo import app
import apollo.lib.settings
from apollo.lib.websocket_manager import WebSocketManager
from apollo.models import Base, init_sqlalchemy, SessionLocal
from apollo.models.agent import Agent
from apollo.models.oauth import OAuthAccessToken, OAuthClient


@fixture
def test_client():
    return TestClient(app)

@fixture
def settings():
    yield apollo.lib.settings.settings
    apollo.lib.settings.settings = {}


@fixture
def db_session(settings):
    try:
        config = ConfigParser()
        config.read('test.ini')
        init_sqlalchemy(config)
        session = SessionLocal()
        yield session
    finally:
        empty_tables()
        session.close()


def empty_tables():
    with contextlib.closing(Base.metadata.bind.connect()) as con:
        trans = con.begin()
        for table in reversed(Base.metadata.sorted_tables):
            con.execute(table.delete())
        trans.commit()


@fixture
def access_token(db_session):
    agent = Agent(
        name='test',
        oauth_client=OAuthClient(
            type='confidential',
            tokens=[OAuthAccessToken()]
        )
    )
    db_session.add(agent)
    db_session.flush()
    access_token_id = agent.oauth_client.tokens[0].id
    db_session.commit()
    return db_session.query(OAuthAccessToken).get(access_token_id)


@fixture
def authenticated_agent_headers(access_token):
    return {
        'authorization': f"Bearer {access_token.access_token}"
    }

