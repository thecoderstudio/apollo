import uuid
import pytest
from pydantic import ValidationError

from apollo.lib.schemas.user import CreateUserSchema, UserSchema
from apollo.models.user import User


def test_create_user_valid(db_session):
    user = CreateUserSchema(username='username ', password='testpass')

    assert user.username == 'username'
    assert user.password == 'testpass'


def test_create_user_username_exists(db_session):
    db_session.add(
        User(username='username', password_hash='hash', password_salt='salt'))
    db_session.commit()
    with pytest.raises(ValueError, match='username must be unique'):
        CreateUserSchema(username="username", password="testpass")


def test_create_user_invalid_password(db_session):
    with pytest.raises(ValidationError, match='at least 8 characters'):
        CreateUserSchema(username='johndoe', password='')


def test_create_user_missing_fields(db_session):
    message = 'field required'
    with pytest.raises(ValidationError, match=message):
        CreateUserSchema(username='johndoe')

    with pytest.raises(ValidationError, match=message):
        CreateUserSchema(password='testpass')


def test_create_user_invalid_username(db_session):
    with pytest.raises(ValidationError,
                       match='ensure this value has at least 1 characters'):
        CreateUserSchema(username=' ', password='testpass')


def test_user_valid(db_session):
    id_ = uuid.uuid4()
    user = UserSchema(id=id_, username='johndoe')

    assert user.id == id_
    assert user.username == 'johndoe'


def test_user_invalid_username(db_session):
    with pytest.raises(ValidationError,
                       match='ensure this value has at least 1 characters'):
        UserSchema(username=' ', password='testpass')
