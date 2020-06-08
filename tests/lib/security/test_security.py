import base64
import datetime
import uuid
from secrets import token_hex

import pytest

from apollo.lib.exceptions.oauth import (
    AuthorizationHeaderNotFound, InvalidAuthorizationMethod,
    InvalidAuthorizationHeader)
from apollo.lib.security import (
    Allow, Deny, Everyone, parse_authorization_header,
    Agent as AgentPrincipal)
from apollo.models.agent import Agent
from apollo.models.oauth import OAuthAccessToken, OAuthClient
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


def test_auth_policy_minimal_principals(mock_policy):
    principals = mock_policy().get_principals({})

    assert principals == [Everyone]


def test_auth_policy_agent_principals(mock_policy, access_token):
    principals = mock_policy().get_principals({
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
def test_auth_policy_principals_malformed_auth_header(mock_policy,
                                                      auth_header):
    principals = mock_policy().get_principals({
        'authorization': auth_header
    })

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

    return policy.get_principals({
        'authorization': f"Bearer {access_token}"
    })


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
def test_check_permission(mock_policy, mock_context_acl_provider, provider_acl,
                          context_acl, expectation):
    allowed = mock_policy(provider_acl).check_permission(
        'public', {}, mock_context_acl_provider(context_acl))

    assert allowed is expectation


def test_check_permission_denied_implicit(mock_policy):
    policy = mock_policy([
        (Allow, Everyone, 'fake'),
        (Allow, 'test', 'public')
    ])
    allowed = policy.check_permission('public', {})

    assert allowed is False


def test_check_permission_invalid_acl(mocker, mock_policy):
    policy = mock_policy([
        ('fake', Everyone, 'public')
    ])

    with pytest.raises(ValueError, match="Invalid action in ACL"):
        policy.check_permission('public', {})


def test_validate_permission_allowed_with_context_provider(
    mock_policy, mock_context_acl_provider
):
    policy = mock_policy([(Deny, Everyone, 'public')])
    policy.validate_permission('public', {}, mock_context_acl_provider(
        [(Allow, Everyone, 'public')]
    ))


def test_validate_permission_denied_explicit_with_context_provider(
    mock_policy, mock_context_acl_provider
):
    policy = mock_policy([(Allow, Everyone, 'public')])
    with raisesHTTPForbidden:
        policy.validate_permission('public', {}, mock_context_acl_provider(
            [(Deny, Everyone, 'public')]
        ))


def test_validate_permission_denied_implicit(mock_policy):
    policy = mock_policy([
        (Allow, Everyone, 'fake'),
        (Allow, 'test', 'public')
    ])
    with raisesHTTPForbidden:
        policy.validate_permission('public', {})


def test_validate_permission_invalid_acl(mock_policy):
    policy = mock_policy([('test', Everyone, 'public')])

    with raisesHTTPForbidden:
        policy.validate_permission('public', {})
