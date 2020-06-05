import datetime

import pytest

from apollo.lib.exceptions import HTTPException
from apollo.lib.router import SecureRouter
from apollo.lib.security import Allow, Agent, Everyone


def test_secure_router_default_acl():
    assert SecureRouter().__acl__() == [(Allow, Everyone, 'public')]


def test_secure_router_additional_acl():
    router = SecureRouter([(Allow, Agent, 'test')])

    assert router.__acl__() == [(Allow, Agent, 'test'),
                                (Allow, Everyone, 'public')]


@pytest.mark.parametrize("permission,auth_header,permitted", [
    ('public', None, True),
    ('public', '', True),
    ('public', 'fake', True),
    ('test', None, False),
    ('test', '', False),
    ('test', 'fake', False),
    ('test',
     "Bearer b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57",
     True)
])
@pytest.mark.asyncio
async def test_websocket_oauth_permissions(mocker, db_session, access_token,
                                           permission, auth_header, permitted):
    access_token.access_token = (
        "b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57"
    )
    db_session.commit()

    router_acl = [(Allow, Agent, 'test')]

    if permitted:
        await call_websocket_decorated_mock(mocker, router_acl, permission,
                                            auth_header)
    else:
        with pytest.raises(HTTPException, match="Permission denied."):
            await call_websocket_decorated_mock(mocker, router_acl, permission,
                                                auth_header)


async def call_websocket_decorated_mock(mocker, router_acl, permission,
                                        auth_header):
    router = SecureRouter(router_acl)

    @router.websocket('/test', permission=permission)
    async def mock(websocket):
        pass

    websocket_mock = mocker.MagicMock()
    websocket_mock.headers = {
        'authorization': auth_header
    }

    await mock(websocket_mock)


@pytest.mark.asyncio
async def test_websocket_oauth_inactive_client(mocker, db_session,
                                               access_token):
    access_token.client.active = False
    db_session.commit()

    with pytest.raises(HTTPException, match="Permission denied."):
        await call_websocket_decorated_mock(
            mocker,
            [(Allow, Agent, 'test')],
            'test',
            f"Bearer {access_token.access_token}"
        )


@pytest.mark.asyncio
async def test_websocket_oauth_expired_token(mocker, db_session, access_token):
    access_token.expiry_date = datetime.datetime.now(datetime.timezone.utc)
    db_session.commit()

    with pytest.raises(HTTPException, match="Permission denied."):
        await call_websocket_decorated_mock(
            mocker,
            [(Allow, Agent, 'test')],
            'test',
            f"Bearer {access_token.access_token}"
        )
