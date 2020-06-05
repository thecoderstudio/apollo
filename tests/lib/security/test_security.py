import base64
import datetime
import uuid
from secrets import token_hex

import pytest

import asserts
from apollo.lib.exceptions.oauth import (
    AuthorizationHeaderNotFound, InvalidAuthorizationMethod,
    InvalidAuthorizationHeader)
from apollo.lib.security import (
    Allow, AuthorizationPolicy, Deny, Everyone, parse_authorization_header,
    Agent as AgentPrincipal)
from apollo.models.agent import Agent
from apollo.models.oauth import OAuthAccessToken, OAuthClient
from tests.lib.security import (
    get_acl_provider_mock, get_authorization_policy_with_mock)


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


def build_credentials_str(method, creds):
    encoded_creds = base64.b64encode(creds.encode('utf-8')).decode('utf-8')
    return f"{method} {encoded_creds}"


def test_auth_policy_minimal_principals(mocker):
    policy = get_authorization_policy_with_mock(mocker)
    principals = policy.get_principals({})

    assert principals == [Everyone]


def test_auth_policy_agent_principals(mocker, access_token):
    policy = get_authorization_policy_with_mock(mocker)
    principals = policy.get_principals({
        'authorization': f"Bearer {access_token.access_token}"
    })

    assert principals == [Everyone, AgentPrincipal,
                          f"agent:{access_token.client_id}"]


@pytest.mark.parametrize('auth_header', [
    "",
    "fake",
    None,
    "Basic b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57",
    "Bearer b8887eefe2179eccb0565674fe196ee12f0621d1d2017a61b195ec17e5d2ac57",
])
def test_auth_policy_principals_malformed_auth_header(mocker, auth_header):
    policy = get_authorization_policy_with_mock(mocker)
    principals = policy.get_principals({
        'authorization': auth_header
    })

    assert principals == [Everyone]


def test_auth_policy_principals_inactive_oauth_client(mocker, db_session):
    agent = Agent(
        name='test',
        oauth_client=OAuthClient(
            type='confidential',
            active=False,
            tokens=[OAuthAccessToken()]
        )
    )
    assert get_principals(mocker, db_session, agent) == [Everyone]


def get_principals(mocker, db_session, agent):
    db_session.add(agent)
    db_session.flush()
    access_token = agent.oauth_client.tokens[0].access_token
    db_session.commit()

    policy = get_authorization_policy_with_mock(mocker)
    return policy.get_principals({
        'authorization': f"Bearer {access_token}"
    })


def test_auth_policy_principals_expired_oauth_token(mocker, db_session):
    agent = Agent(
        name='test',
        oauth_client=OAuthClient(
            type='confidential',
            tokens=[OAuthAccessToken(
                expiry_date=datetime.datetime.now(datetime.timezone.utc)
            )]
        )
    )

    assert get_principals(mocker, db_session, agent) == [Everyone]


def test_get_complete_acl_no_context_provider(mocker):
    policy = get_authorization_policy_with_mock(mocker, [
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
def test_get_comple_acl(mocker, provider_acl, context_acl, expected_acl):
    context_acl_provider_mock = mocker.MagicMock(
        __acl__=mocker.MagicMock(return_value=context_acl)
    )
    policy = get_authorization_policy_with_mock(mocker, provider_acl)
    acl = policy.get_complete_acl(context_acl_provider_mock)

    assert acl == expected_acl


@pytest.mark.parametrize(
    "provider_acl,context_acl,expectation",
    acl_permission_expectations
)
def test_check_permission(mocker, provider_acl, context_acl, expectation):
    context_acl_provider_mock = mocker.MagicMock(
        __acl__=mocker.MagicMock(return_value=context_acl)
    )
    policy = get_authorization_policy_with_mock(mocker, provider_acl)

    allowed = policy.check_permission('public', {}, context_acl_provider_mock)

    assert allowed is expectation


def test_check_permission_denied_implicit(mocker):
    policy = get_authorization_policy_with_mock(mocker, [
        (Allow, Everyone, 'fake'),
        (Allow, 'test', 'public')
    ])
    allowed = policy.check_permission('public', {})

    assert allowed is False


def test_check_permission_invalid_acl(mocker):
    policy = get_authorization_policy_with_mock(mocker, [
        (Allow, 'test', 'public')
    ])

    # TODO change to custom exception
    with pytest.raises(ValueError):
        policy.check_permission('public', {})


def test_validate_permission_allowed_with_context_provider(mocker):
    acl_provider_mock = mocker.MagicMock(
        __acl__=mocker.MagicMock(return_value=[
            (Deny, Everyone, 'public')
        ])
    )
    context_acl_provider_mock = mocker.MagicMock(
        __acl__=mocker.MagicMock(return_value=[
            (Allow, Everyone, 'public')
        ])
    )
    policy = AuthorizationPolicy(acl_provider_mock)
    policy.validate_permission('public', {}, context_acl_provider_mock)


def test_validate_permission_denied_explicit_with_context_provider(mocker):
    acl_provider_mock = mocker.MagicMock(
        __acl__=mocker.MagicMock(return_value=[
            (Allow, Everyone, 'public')
        ])
    )
    context_acl_provider_mock = mocker.MagicMock(
        __acl__=mocker.MagicMock(return_value=[
            (Deny, Everyone, 'public')
        ])
    )
    policy = AuthorizationPolicy(acl_provider_mock)
    with asserts.raisesHTTPForbidden:
        policy.validate_permission('public', {}, context_acl_provider_mock)


def test_validate_permission_denied_implicit(mocker):
    acl_provider_mock = mocker.MagicMock(
        __acl__=mocker.MagicMock(return_value=[
            (Allow, Everyone, 'fake'),
            (Allow, 'test', 'public')
        ])
    )
    policy = AuthorizationPolicy(acl_provider_mock)
    with asserts.raisesHTTPForbidden:
        policy.validate_permission('public', {})


def test_validate_permission_invalid_acl(mocker):
    acl_provider_mock = mocker.MagicMock(
        __acl__=mocker.MagicMock(return_value=[
            ('test', Everyone, 'public')
        ])
    )
    policy = AuthorizationPolicy(acl_provider_mock)

    # TODO change to custom exception
    with asserts.raisesHTTPForbidden:
        policy.validate_permission('public', {})
