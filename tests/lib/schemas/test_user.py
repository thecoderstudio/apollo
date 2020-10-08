import uuid

import pytest
from pydantic import ValidationError

from apollo.lib.schemas.user import (CreateUserSchema, UserSchema,
                                     UpdateUserSchema)
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


def test_create_user_password_too_short(db_session):
    with pytest.raises(ValidationError, match='at least 8 characters'):
        CreateUserSchema(username='johndoe', password='')


def test_create_user_password_contains_whitespace(db_session):
    with pytest.raises(ValueError,
                       match="field can't contain whitespaces"):
        CreateUserSchema(username='johndoe', password='pass word')


def test_update_user_valid():
    user = UpdateUserSchema(username='newusername', password='password',
                            password_confirm='password',
                            old_password='oldpassword')

    assert user.password == 'password'
    assert user.old_password == 'oldpassword'
    assert user.password_confirm == 'password'


@pytest.mark.parametrize('values', [
    {
        'password': 'pass word',
        'old_password': 'testtest',
        'password_confirm': 'pass word'
    },
    {
        'username': 'user name'
    },
])
def test_update_user_field_contains_whitespace(values):
    with pytest.raises(ValueError,
                       match="field can't contain whitespaces"):
        UpdateUserSchema(**values)


def test_update_user_password_contains_whitespace():
    with pytest.raises(ValueError,
                       match="field can't contain whitespaces"):
        UpdateUserSchema(password='pass word', old_password='testtest',
                         password_confirm='pass word')


def test_update_user_passwords_do_not_match():
    with pytest.raises(ValueError,
                       match="passwords must match"):
        UpdateUserSchema(password='password', old_password='testtest',
                         password_confirm='wrongpassword')


def test_update_password_old_password_required():
    with pytest.raises(
        ValueError,
        match="old password is required when password is given"
    ):
        UpdateUserSchema(password='password', password_confirm='password')


def test_update_password_password_confirm_required():
    with pytest.raises(
        ValueError,
        match="password confirm is required when password is given"
    ):
        UpdateUserSchema(password='password', old_password='old_password')


def test_update_user_old_and_new_password_identical():
    with pytest.raises(ValueError,
                       match="password cannot match old password"):
        UpdateUserSchema(password='password', password_confirm='password',
                         old_password='password')


def test_update_user_no_unique_username(db_session, user):
    with pytest.raises(ValueError,
                       match="username must be unique"):
        UpdateUserSchema(username='test_admin')


def test_update_user_username_too_short(db_session):
    with pytest.raises(ValidationError,
                       match='ensure this value has at least 1 characters'):
        UpdateUserSchema(username='')


def test_update_user_username_too_long(db_session):
    with pytest.raises(ValidationError,
                       match='ensure this value has at most 36 characters'):
        UpdateUserSchema(username='johndoeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')


def test_create_user_missing_fields(db_session):
    message = 'field required'
    with pytest.raises(ValidationError, match=message):
        CreateUserSchema(username='johndoe')

    with pytest.raises(ValidationError, match=message):
        CreateUserSchema(password='testpass')


def test_create_user_username_too_short(db_session):
    with pytest.raises(ValidationError,
                       match='ensure this value has at least 1 characters'):
        CreateUserSchema(username=' ', password='testpass')


def test_create_user_username_too_long(db_session):
    with pytest.raises(ValidationError,
                       match='ensure this value has at most 36 characters'):
        CreateUserSchema(username='johndoeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
                         password='testpass')


def test_user_valid(db_session):
    id_ = uuid.uuid4()
    user = UserSchema(id=id_, username='johndoe',
                      has_changed_initial_password=False)

    assert user.id == id_
    assert user.username == 'johndoe'
    assert user.has_changed_initial_password is False
