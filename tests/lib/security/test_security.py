import base64
import datetime
import uuid
from secrets import token_hex

import pytest

from apollo.lib.exceptions.oauth import (
    AuthorizationHeaderNotFound, InvalidAuthorizationMethod,
    InvalidAuthorizationHeader)
from apollo.lib.security import (
    Allow, Authenticated, Deny, Everyone, get_auth_method_and_token,
    get_client_id_from_authorization_header, Human, parse_authorization_header,
    Agent as AgentPrincipal, Uninitialized)
from apollo.models.agent import Agent
from apollo.models.oauth import OAuthAccessToken, OAuthClient
from tests import create_http_connection_mock
from tests.asserts import raisesHTTPForbidden


agent_id = str(uuid.uuid4())
secret = token_hex(32)

# [provider_acl, context_acl, permitted_expectation]
acl_permission_expectations = [
    [
        [(Deny, Everyone, 'public')],
        [(Allow, Everyone, 'public')],
        True
    ],
    [
        [(Allow, Everyone, 'public')],
        [(Deny, Everyone, 'public')],
        False
    ]
]


def test_enhance_http_connection(mock_policy, http_connection_mock,
                                 db_session):
    enhanced_http_connection = mock_policy().enhance_http_connection(
        http_connection_mock, db_session)

    assert enhanced_http_connection.current_user is None
    assert enhanced_http_connection.oauth_client is None


def test_enhance_http_connection_authenticated(
    mock_policy,
    mock_http_connection,
    db_session,
    user,
    access_token,
    session_cookie
):
    http_connection = mock_http_connection(
        cookies=session_cookie,
        headers={'authorization': f"Bearer {access_token.access_token}"}
    )

    enhanced_http_connection = mock_policy().enhance_http_connection(
        http_connection, db_session)

    assert enhanced_http_connection.current_user == user
    assert enhanced_http_connection.oauth_client == access_token.client


def test_parse_valid_authorization_header():
    authorization = build_credentials_str(
        'Basic',
        f"{agent_id}:{secret}"
    )
    parsed = parse_authorization_header(authorization)
    assert agent_id == parsed['agent_id']
    assert secret == parsed['secret']


def test_parse_missing_authorization_header():
    with pytest.raises(AuthorizationHeaderNotFound):
        parse_authorization_header(None)


def test_parse_authorization_header_wrong_method():
    authorization = build_credentials_str(
        'Bearer',
        f"{agent_id}:{secret}"
    )
    with pytest.raises(InvalidAuthorizationMethod):
        parse_authorization_header(authorization)


def test_parse_malformed_authorization_header():
    authorization = build_credentials_str('Basic', "test value")
    with pytest.raises(InvalidAuthorizationHeader):
        parse_authorization_header(authorization)

    authorization = ""
    with pytest.raises(InvalidAuthorizationHeader):
        parse_authorization_header(authorization)


def build_credentials_str(method, creds):
    encoded_creds = base64.b64encode(creds.encode('utf-8')).decode('utf-8')
    return f"{method} {encoded_creds}"


def test_auth_policy_minimal_principals(mock_policy, http_connection_mock):
    principals = mock_policy().get_principals(http_connection_mock)

    assert principals == [Everyone]


def test_auth_policy_agent_principals(mock_policy, access_token,
                                      mock_http_connection, db_session):
    policy = mock_policy()
    principals = policy.get_principals(
        policy.enhance_http_connection(mock_http_connection(headers={
            'authorization': f"Bearer {access_token.access_token}"
        }), db_session)
    )

    assert principals == [Everyone, Authenticated, AgentPrincipal,
                          f"agent:{access_token.client_id}"]


def test_auth_policy_admin_user_principals(mock_policy, mock_http_connection,
                                           user, session_cookie, db_session):
    policy = mock_policy()
    principals = policy.get_principals(
        policy.enhance_http_connection(mock_http_connection(
            cookies=session_cookie
        ), db_session)
    )

    assert principals == [Everyone, Authenticated, Human, f"user:{user.id}",
                          'role:admin']


def test_auth_policy_default_user_principals(mock_policy, mock_http_connection,
                                             user, session_cookie, db_session):
    user.role = None
    db_session.commit()
    policy = mock_policy()
    principals = policy.get_principals(
        policy.enhance_http_connection(mock_http_connection(
            cookies=session_cookie
        ), db_session)
    )

    assert principals == [Everyone, Authenticated, Human, f"user:{user.id}"]


def test_auth_policy_default_uninitialized_user_principals(
    mock_policy, mock_http_connection, uninitialized_user,
    session_cookie_for_uninitialized_user, db_session
):
    uninitialized_user.role = None
    db_session.commit()
    policy = mock_policy()
    principals = policy.get_principals(
        policy.enhance_http_connection(mock_http_connection(
            cookies=session_cookie_for_uninitialized_user
        ), db_session)
    )

    assert principals == [Everyone, Uninitialized]


@pytest.mark.parametrize('auth_header', [
    "",
    "fake",
    None,
    "Basic b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57",
    "Bearer b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57",
])
def test_auth_policy_principals(
    mock_policy, mock_http_connection, auth_header
):
    principals = mock_policy().get_principals(mock_http_connection(headers={
        'authorization': auth_header
    }))

    assert principals == [Everyone]


def test_auth_policy_principals_inactive_oauth_client(mock_policy, db_session):
    agent = Agent(
        name='test',
        oauth_client=OAuthClient(
            type='confidential',
            active=False,
            tokens=[OAuthAccessToken()]
        )
    )
    assert get_principals(mock_policy(), db_session, agent) == [Everyone]


def get_principals(policy, db_session, agent):
    db_session.add(agent)
    db_session.flush()
    access_token = agent.oauth_client.tokens[0].access_token
    db_session.commit()

    return policy.get_principals(create_http_connection_mock(headers={
        'authorization': f"Bearer {access_token}"
    }))


def test_auth_policy_principals_expired_oauth_token(mock_policy, db_session):
    agent = Agent(
        name='test',
        oauth_client=OAuthClient(
            type='confidential',
            tokens=[OAuthAccessToken(
                expiry_date=datetime.datetime.now(datetime.timezone.utc)
            )]
        )
    )

    assert get_principals(mock_policy(), db_session, agent) == [Everyone]


def test_get_complete_acl_no_context_provider(mock_policy):
    policy = mock_policy([
        (Allow, Everyone, 'public')
    ])

    assert policy.get_complete_acl() == [
        (Allow, Everyone, 'public')
    ]


@pytest.mark.parametrize(
    "provider_acl,context_acl,expected_acl",
    [
        [
            [(Allow, Everyone, 'public')],
            [],
            [(Allow, Everyone, 'public')]
        ],
        [
            [(Allow, Everyone, 'public')],
            [(Allow, 'test', 'fake')],
            [(Allow, 'test', 'fake'), (Allow, Everyone, 'public')]
        ]
    ]
)
def test_get_comple_acl(mock_policy, mock_context_acl_provider, provider_acl,
                        context_acl, expected_acl):
    acl = mock_policy(provider_acl).get_complete_acl(
        mock_context_acl_provider(context_acl)
    )

    assert acl == expected_acl


@pytest.mark.parametrize(
    "provider_acl,context_acl,expectation",
    acl_permission_expectations
)
def test_check_permission(
    mock_policy, http_connection_mock, mock_context_acl_provider,
    provider_acl, context_acl, expectation
):
    allowed = mock_policy(provider_acl).check_permission(
        'public',
        http_connection_mock,
        mock_context_acl_provider(context_acl)
    )

    assert allowed is expectation


def test_check_permission_denied_implicit(mock_policy, http_connection_mock):
    policy = mock_policy([
        (Allow, Everyone, 'fake'),
        (Allow, 'test', 'public')
    ])
    allowed = policy.check_permission('public', http_connection_mock)

    assert allowed is False


def test_check_permission_invalid_acl(mocker, mock_policy,
                                      http_connection_mock):
    policy = mock_policy([
        ('fake', Everyone, 'public')
    ])

    with pytest.raises(ValueError, match="Invalid action in ACL"):
        policy.check_permission('public', http_connection_mock)


def test_validate_permission_allowed_with_context_provider(
    mock_policy, mock_context_acl_provider, http_connection_mock
):
    policy = mock_policy([(Deny, Everyone, 'public')])
    policy.validate_permission(
        'public',
        http_connection_mock,
        mock_context_acl_provider([(Allow, Everyone, 'public')])
    )


def test_validate_permission_denied_explicit_with_context_provider(
    mock_policy, mock_context_acl_provider, http_connection_mock
):
    policy = mock_policy([(Allow, Everyone, 'public')])
    with raisesHTTPForbidden:
        policy.validate_permission(
            'public',
            http_connection_mock,
            mock_context_acl_provider([(Deny, Everyone, 'public')])
        )


def test_validate_permission_denied_implicit(mock_policy,
                                             http_connection_mock):
    policy = mock_policy([
        (Allow, Everyone, 'fake'),
        (Allow, 'test', 'public')
    ])
    with raisesHTTPForbidden:
        policy.validate_permission('public', http_connection_mock)


def test_validate_permission_invalid_acl(mock_policy, http_connection_mock):
    policy = mock_policy([('test', Everyone, 'public')])

    with raisesHTTPForbidden:
        policy.validate_permission('public', http_connection_mock)


@pytest.mark.parametrize('authorization, expected', [
    ("Bearer 123", ('Bearer', '123')),
    ("", (None, None)),
    (None, (None, None))
])
def test_get_auth_method_and_token_success(authorization, expected):
    assert get_auth_method_and_token(authorization) == expected


@pytest.mark.parametrize('token, expected_id', [
    ('e678cd491f837f4e2317a6c60ac0b0c6033d863633ab48da542aa6b72a366dec',
     'd10b92dc-521b-45e9-bf4b-69dc55a26c19'),
    ('fake token', None)
])
def test_get_client_id_from_authorization_header(db_session, token,
                                                 expected_id):
    agent = Agent(
        id='d10b92dc-521b-45e9-bf4b-69dc55a26c19',
        name='test',
        oauth_client=OAuthClient(
            type='confidential',
            tokens=[
                OAuthAccessToken(
                    access_token=('e678cd491f837f4e2317a6c60ac0b0c603'
                                  + '3d863633ab48da542aa6b72a366dec')
                )
            ]
        )
    )
    db_session.add(agent)
    db_session.commit()
    assert str(get_client_id_from_authorization_header(
        db_session, f'bearer {token}')) == str(expected_id)
