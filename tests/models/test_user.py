import pytest
from sqlalchemy.exc import DataError

from apollo.models.user import User, get_user_by_username


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


def test_user_invalid_username(db_session):
    user = User(
        username='johndoeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
        password_hash=(
            '$2b$12$FdTnxaL.NlRdEHREzbU3k.Nt1Gpii9vrKU.1h/MnZYdlMHPUW8/k.'),
        password_salt='$2b$12$FdTnxaL.NlRdEHREzbU3k.'
    )
    with pytest.raises(DataError):
        db_session.add(user)
        db_session.commit()
