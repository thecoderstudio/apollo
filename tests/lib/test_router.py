import datetime
import pytest

from apollo.lib.router import SecureRouter
from apollo.lib.security import Allow, Agent, Authenticated, Everyone, Human
from tests import create_http_connection_mock
from tests.asserts import raisesHTTPForbidden

oauth_permission_expectations = [
    ('public', None, True),
    ('public', '', True),
    ('public', 'fake', True),
    ('test', None, False),
    ('test', '', False),
    ('test', 'fake', False),
    ('test',
     "Bearer b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57",
     True),
    ('authenticated', None, False),
    ('authenticated', '', False),
    ('authenticated', 'fake', False),
    ('authenticated',
     "Bearer b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57",
     True),
    ('human', None, False),
    ('human', '', False),
    ('human', 'fake', False),
    ('human',
     "Bearer b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57",
     False)
]

# permission, authenticated, role, expected result
cookie_permission_expectations = [
    ('public', False, None, True),
    ('authenticated', False, None, False),
    ('human', False, None, False),
    ('admin', False, None, False),
    ('public', True, None, True),
    ('authenticated', True, None, True),
    ('human', True, None, True),
    ('admin', True, None, False),
    ('public', True, 'admin', True),
    ('authenticated', True, 'admin', True),
    ('human', True, 'admin', True),
    ('admin', True, 'admin', True),
    ('admin_no_access', True, 'admin', False),
]

testable_http_methods = [
    'post', 'put', 'patch', 'delete', 'get', 'options', 'trace', 'head'
]


def test_secure_router_default_acl():
    assert SecureRouter().__acl__() == [(Allow, Everyone, 'public')]


def test_secure_router_additional_acl():
    router = SecureRouter([(Allow, Agent, 'test')])

    assert router.__acl__() == [(Allow, Agent, 'test'),
                                (Allow, Everyone, 'public')]


@pytest.mark.parametrize("permission,auth_header,permitted",
                         oauth_permission_expectations)
@pytest.mark.parametrize('http_method', testable_http_methods)
def test_secure_router_http_methods_oauth_permissions(
    db_session, access_token, permission, auth_header, permitted, http_method
):
    access_token.access_token = (
        "b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57"
    )
    db_session.commit()

    router_acl = [
        (Allow, Agent, 'test'),
        (Allow, Authenticated, 'authenticated'),
        (Allow, Human, 'human')
    ]
    request_mock = create_http_connection_mock(headers={
        'authorization': auth_header
    })

    if permitted:
        call_http_method_decorated_mock(http_method, router_acl, permission,
                                        request_mock)
    else:
        with raisesHTTPForbidden:
            call_http_method_decorated_mock(http_method, router_acl,
                                            permission, request_mock)


def call_http_method_decorated_mock(http_method, router_acl, permission,
                                    request_mock):
    router = SecureRouter(router_acl)
    route_decorator = getattr(router, http_method)

    @route_decorator('/test', permission=permission)
    def endpoint_mock():
        pass

    endpoint_mock(request=request_mock)


@pytest.mark.parametrize("permission,authenticated,role,permitted",
                         cookie_permission_expectations)
@pytest.mark.parametrize('http_method', testable_http_methods)
def test_secure_router_http_methods_cookie_permissions(
    db_session, user, session_cookie, permission, authenticated, role,
    permitted, http_method
):
    router_acl, request_mock = generate_http_test_parameters(
        db_session, user, authenticated, session_cookie, role)

    if permitted:
        call_http_method_decorated_mock(http_method, router_acl, permission,
                                        request_mock)
    else:
        with raisesHTTPForbidden:
            call_http_method_decorated_mock(http_method, router_acl,
                                            permission, request_mock)


def generate_http_test_parameters(db_session, user, authenticated,
                                  session_cookie, role):
    if role != 'admin':
        user.role = None

    if not authenticated:
        session_cookie = {}

    db_session.commit()

    router_acl = [
        (Allow, Authenticated, 'authenticated'),
        (Allow, Human, 'human'),
        (Allow, 'role:admin', 'admin'),
        (Allow, 'nobody', 'admin_no_access')
    ]
    connection_mock = create_http_connection_mock(cookies=session_cookie)

    return (router_acl, connection_mock)


@pytest.mark.parametrize("permission,auth_header,permitted",
                         oauth_permission_expectations)
@pytest.mark.asyncio
async def test_websocket_oauth_permissions(db_session, access_token,
                                           permission, auth_header, permitted):
    access_token.access_token = (
        "b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57"
    )
    db_session.commit()

    router_acl = [
        (Allow, Agent, 'test'),
        (Allow, Authenticated, 'authenticated'),
        (Allow, Human, 'human')
    ]
    websocket_mock = create_http_connection_mock(headers={
        'authorization': auth_header
    })

    if permitted:
        await call_websocket_decorated_mock(router_acl, permission,
                                            websocket_mock)
    else:
        with raisesHTTPForbidden:
            await call_websocket_decorated_mock(router_acl, permission,
                                                websocket_mock)


async def call_websocket_decorated_mock(router_acl, permission,
                                        websocket_mock):
    router = SecureRouter(router_acl)

    @router.websocket('/test', permission=permission)
    async def mock(websocket):
        pass

    await mock(websocket_mock)


@pytest.mark.parametrize("permission,authenticated,role,permitted",
                         cookie_permission_expectations)
@pytest.mark.asyncio
async def test_websocket_cookie_permissions(
    db_session, user, session_cookie, permission, authenticated, role,
    permitted
):
    router_acl, websocket_mock = generate_http_test_parameters(
        db_session, user, authenticated, session_cookie, role)

    if permitted:
        await call_websocket_decorated_mock(router_acl, permission,
                                            websocket_mock)
    else:
        with raisesHTTPForbidden:
            await call_websocket_decorated_mock(router_acl, permission,
                                                websocket_mock)


@pytest.mark.asyncio
async def test_websocket_oauth_inactive_client(db_session, access_token,
                                               http_connection_mock):
    access_token.client.active = False
    db_session.commit()

    http_connection_mock.headers = {
        'authorization': f"Bearer {access_token.access_token}"
    }

    with raisesHTTPForbidden:
        await call_websocket_decorated_mock(
            [(Allow, Agent, 'test')],
            'test',
            http_connection_mock
        )


@pytest.mark.asyncio
async def test_websocket_oauth_expired_token(db_session, access_token,
                                             http_connection_mock):
    access_token.expiry_date = datetime.datetime.now(datetime.timezone.utc)
    db_session.commit()

    http_connection_mock.headers = {
        'authorization': f"Bearer {access_token.access_token}"
    }

    with raisesHTTPForbidden:
        await call_websocket_decorated_mock(
            [(Allow, Agent, 'test')],
            'test',
            http_connection_mock
        )
