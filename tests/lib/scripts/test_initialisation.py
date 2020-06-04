from apollo.lib.scripts.initialisation import (random_password,
                                               add_admin_user,
                                               initialise_if_needed)
from apollo.models.user import get_user_by_username


def test_initialise_if_needed(mocker, db_session):
    add_admin_user = mocker.patch(
        'apollo.lib.scripts.initialisation.add_admin_user')

    initialise_if_needed()
    add_admin_user.assert_called_once()


def test_add_admin_user(db_session):
    add_admin_user(db_session)

    assert get_user_by_username(
        session=db_session, username='admin') is not None
