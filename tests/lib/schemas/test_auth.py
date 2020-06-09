import pytest
from pydantic import ValidationError

from apollo.lib.schemas.auth import LoginSchema


def test_valid_login_schema():
    login_data = LoginSchema(username='username ', password='password ')

    assert login_data.username == 'username'
    assert login_data.password == 'password'


def test_login_schema_missing_fields():
    message = 'field required'
    with pytest.raises(ValidationError, match=message):
        LoginSchema(username='johndoe')

    with pytest.raises(ValidationError, match=message):
        LoginSchema(password='testpass')
