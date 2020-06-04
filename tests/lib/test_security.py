import base64
import uuid
from secrets import token_hex

import pytest

from apollo.lib.exceptions.oauth import (
    AuthorizationHeaderNotFound, InvalidAuthorizationMethod,
    InvalidAuthorizationHeader)
from apollo.lib.security import (Allow, AuthorizationPolicy, Everyone,
                                 parse_authorization_header)

agent_id = str(uuid.uuid4())
secret = token_hex(32)


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
    policy = AuthorizationPolicy(mocker.MagicMock())
    principals = policy.get_principals()

    assert principals == (Everyone,)


def test_get_complete_acl_no_context_provider(mocker):
    acl_provider_mock = mocker.MagicMock(
        __acl__=mocker.MagicMock(return_value=[
            (Allow, Everyone, 'public')
        ])
    )
    policy = AuthorizationPolicy(acl_provider_mock)

    assert policy.get_complete_acl() == [
        (Allow, Everyone, 'public')
    ]


def test_get_complete_acl_with_context_provider(mocker):
    acl_provider_mock = mocker.MagicMock(
        __acl__=mocker.MagicMock(return_value=[
            (Allow, Everyone, 'public')
        ])
    )
    context_acl_provider_mock = mocker.MagicMock(
        __acl__=mocker.MagicMock(return_value=[
            (Allow, 'test', 'fake')
        ])
    )
    policy = AuthorizationPolicy(acl_provider_mock)
    acl = policy.get_complete_acl(context_acl_provider_mock)

    assert acl == [(Allow, Everyone, 'public'), (Allow, 'test', 'fake')]
