import pytest
from sqlalchemy.exc import DataError

from apollo.models.role import Role
from apollo.models.user import (User, get_user_by_username, count_users,
                                list_users)


def test_get_user_by_name(db_session):
    user = User(
        username='johndoe',
        password_hash=(
            '$2b$12$FdTnxaL.NlRdEHREzbU3k.Nt1Gpii9vrKU.1h/MnZYdlMHPUW8/k.'),
        password_salt='$2b$12$FdTnxaL.NlRdEHREzbU3k.'
    )

    db_session.add(user)
    db_session.flush()
    user_id = user.id
    db_session.commit()

    assert get_user_by_username(db_session, 'johndoe').id == user_id


def test_count_users(db_session):
    assert count_users(db_session) == 0

    user = User(
        username='johndoe',
        password_hash=(
            '$2b$12$FdTnxaL.NlRdEHREzbU3k.Nt1Gpii9vrKU.1h/MnZYdlMHPUW8/k.'),
        password_salt='$2b$12$FdTnxaL.NlRdEHREzbU3k.'
    )

    db_session.add(user)
    db_session.commit()

    assert count_users(db_session) == 1


def test_get_user_by_name_not_found(db_session):
    user = User(
        username='johndoe',
        password_hash=(
            '$2b$12$FdTnxaL.NlRdEHREzbU3k.Nt1Gpii9vrKU.1h/MnZYdlMHPUW8/k.'),
        password_salt='$2b$12$FdTnxaL.NlRdEHREzbU3k.'
    )

    db_session.add(user)
    db_session.commit()

    assert get_user_by_username(db_session, 'notjohndoe') is None


def test_user_username_too_long(db_session):
    user = User(
        username='johndoeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
        password_hash=(
            '$2b$12$FdTnxaL.NlRdEHREzbU3k.Nt1Gpii9vrKU.1h/MnZYdlMHPUW8/k.'),
        password_salt='$2b$12$FdTnxaL.NlRdEHREzbU3k.'
    )
    with pytest.raises(DataError):
        db_session.add(user)
        db_session.commit()


def test_user_cascades(db_session):
    user = User(
        username='johndoe',
        password_hash=(
            '$2b$12$FdTnxaL.NlRdEHREzbU3k.Nt1Gpii9vrKU.1h/MnZYdlMHPUW8/k.'),
        password_salt='$2b$12$FdTnxaL.NlRdEHREzbU3k.',
        role=Role(name='test role')
    )
    db_session.add(user)
    db_session.flush()
    user_id = user.id
    role_id = user.role.id

    persisted_user = db_session.query(User).get(user_id)
    db_session.delete(persisted_user)
    db_session.commit()

    assert db_session.query(Role).get(role_id) is not None


def test_list_users(db_session):
    user_1 = User(
        username='johndoe',
        password_hash=(
            '$2b$12$FdTnxaL.NlRdEHREzbU3k.Nt1Gpii9vrKU.1h/MnZYdlMHPUW8/k.'),
        password_salt='$2b$12$FdTnxaL.NlRdEHREzbU3k.'
    )
    user_2 = User(
        username='jeffjefferson',
        password_hash=(
            '$2b$12$FdTnxaL.NlRdEHREzbU3k.Nt1Gpii9vrKU.1h/MnZYdlMHPUW8/k.'),
        password_salt='$2b$12$FdTnxaL.NlRdEHREzbU3k.'
    )
    db_session.add(user_1)
    db_session.add(user_2)
    db_session.commit()

    users = list_users(db_session)

    assert user_1 in users
    assert user_2 in users
    assert len(users) == 2
