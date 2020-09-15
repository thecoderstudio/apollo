import contextlib
from configparser import ConfigParser
from unittest.mock import AsyncMock

from async_asgi_testclient import TestClient as AsyncTestClient
from fastapi import WebSocket
from fastapi.testclient import TestClient
from pytest import fixture
from starlette.websockets import WebSocketState, WebSocketDisconnect

import apollo.lib.settings
from apollo import app
from apollo.lib.hash import hash_plaintext
from apollo.lib.security import create_session_cookie
from apollo.lib.websocket import WebSocketManager
from apollo.lib.websocket.agent import AgentConnectionManager
from apollo.lib.websocket.app import AppConnectionManager
from apollo.lib.websocket.user import UserConnectionManager, UserConnection
from apollo.models import Base, init_sqlalchemy, SessionLocal
from apollo.models.agent import Agent
from apollo.models.oauth import OAuthAccessToken, OAuthClient
from apollo.models.role import Role
from apollo.models.user import User
from tests import create_http_connection_mock


def _create_and_return_user(has_changed_initial_password=True):
    password_hash, password_salt = hash_plaintext('testing123')
    user = User(
        id='ccaf8799-b134-4e47-82f1-a4d9a207c040',
        username='test_admin',
        password_hash=password_hash,
        password_salt=password_salt,
        role=db_session.query(Role).filter(Role.name == 'admin').one(),
        has_changed_initial_password=has_changed_initial_password
    )
    db_session.add(user)
    db_session.flush()
    user_id = user.id
    db_session.commit()
    return user_id, db_session.query(User).get(user_id)


@fixture
def test_client():
    return TestClient(app)


@fixture
async def async_test_client():
    async with AsyncTestClient(app) as test_client:
        yield test_client


@fixture
def patched_settings(mocker):
    mocker.patch('apollo.lib.settings.settings', {})
    yield apollo.lib.settings.settings
    apollo.lib.settings.settings = {}


@fixture
def connection(patched_settings):
    try:
        config = ConfigParser()
        config.read('test.ini')
        connection = init_sqlalchemy(config).connect()
        yield connection
    finally:
        connection.close()


@fixture
def db_session(connection):
    try:
        empty_tables()
        session = SessionLocal()
        session.add(Role(name='admin'))
        session.commit()
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
    return _create_and_return_user()


@fixture
def unitialized_user(db_session):
    return _create_and_return_user(has_changed_initial_password=False)


@fixture
def session_cookie(user):
    key_name, cookie = create_session_cookie(user)
    return {key_name: cookie}


@fixture
def session_cookie_for_uninitialized_user(uninitialized_user):
    key_name, cookie = create_session_cookie(uninitialized_user)
    return {key_name: cookie}


@fixture
def mock_http_connection():
    return create_http_connection_mock


@fixture
def http_connection_mock(mock_http_connection):
    return mock_http_connection()


@fixture
def websocket_mock(mocker):
    mock = mocker.create_autospec(WebSocket)

    mock._receive = AsyncMock(
        side_effect=WebSocketDisconnect
    )
    mock._send = AsyncMock()
    mock.scope = {'type': 'websocket'}
    mock.client_state = WebSocketState.CONNECTED
    mock.application_state = WebSocketState.CONNECTING
    return mock


@fixture
def user_connection_mock(mocker):
    return mocker.create_autospec(UserConnection)


@fixture
def websocket_manager():
    _wipe_websocket_manager()
    yield WebSocketManager()
    _wipe_websocket_manager()


def _wipe_websocket_manager():
    manager = WebSocketManager()
    manager.open_agent_connections = {}
    manager.open_user_connections = {}
    manager.open_app_connections = {}


@fixture
def agent_connection_manager(websocket_manager):
    manager = AgentConnectionManager()
    manager.websocket_manager = websocket_manager
    return manager


@fixture
def user_connection_manager(websocket_manager):
    manager = UserConnectionManager()
    manager.websocket_manager = websocket_manager
    return manager


# autouse set to true so that the interested agents get wiped so that the
# test doesn't need to know when the app_connection_manager is getting called.
@fixture(autouse=True)
def app_connection_manager(websocket_manager):
    manager = AppConnectionManager()
    manager.interested_connections = {}
    manager.websocket_manager = websocket_manager
    yield manager
    manager.interested_connections = {}
