import base64
import uuid
from secrets import token_hex

import pytest

from apollo.lib.exceptions.oauth import (
    AuthorizationHeaderNotFound, InvalidAuthorizationMethod,
    InvalidAuthorizationHeader)
from apollo.lib.security import parse_authorization_header

agent_id = str(uuid.uuid4())
client_secret = token_hex(32)


def test_parse_valid_authorization_header():
    authorization = build_credentials_str(
        'Basic',
        f"{agent_id}:{client_secret}"
    )
    parsed = parse_authorization_header(authorization)
    assert agent_id == parsed['agent_id']
    assert client_secret == parsed['client_secret']


def test_parse_missing_authorization_header():
    with pytest.raises(AuthorizationHeaderNotFound):
        parse_authorization_header(None)


def test_parse_authorization_header_wrong_method():
    authorization = build_credentials_str(
        'Bearer',
        f"{agent_id}:{client_secret}"
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
