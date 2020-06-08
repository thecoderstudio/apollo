import contextlib
from configparser import ConfigParser

from pytest import fixture

import apollo.lib.settings
from apollo.lib.hash import hash_plaintext
from apollo.lib.security import create_session_cookie
from apollo.models import Base, init_sqlalchemy, SessionLocal
from apollo.models.agent import Agent
from apollo.models.oauth import OAuthAccessToken, OAuthClient
from apollo.models.user import User
from tests import create_http_connection_mock


@fixture
def patched_settings(mocker):
    mocker.patch('apollo.lib.settings.settings', {})
    yield apollo.lib.settings.settings
    apollo.lib.settings.settings = {}


@fixture
def db_session(patched_settings):
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


@fixture
def user(db_session):
    password_hash, password_salt = hash_plaintext('testing123')
    user = User(
        username='test_admin',
        password_hash=password_hash,
        password_salt=password_salt
    )
    db_session.add(user)
    db_session.flush()
    user_id = user.id
    db_session.commit()
    return db_session.query(User).get(user_id)


@fixture
def session_cookie(user):
    key_name, cookie = create_session_cookie(user)
    return {key_name: cookie}


@fixture
def mock_http_connection():
    return create_http_connection_mock


@fixture
def http_connection_mock(mock_http_connection):
    return mock_http_connection()
