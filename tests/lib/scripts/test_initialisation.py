from apollo.lib.initialisation import add_admin_user, initialise_if_needed
from apollo.models.user import get_user_by_username, User


def test_initialise_if_needed(mocker, db_session):
    add_admin_user = mocker.patch(
        'apollo.lib.initialisation.add_admin_user')

    initialise_if_needed()
    add_admin_user.assert_called_once()


def test_initialise_if_needed_not_called(mocker, db_session):
    user = User(
        username='johndoe',
        password_hash=(
            '$2b$12$FdTnxaL.NlRdEHREzbU3k.Nt1Gpii9vrKU.1h/MnZYdlMHPUW8/k.'),
        password_salt='$2b$12$FdTnxaL.NlRdEHREzbU3k.'
    )

    db_session.add(user)
    db_session.commit()

    add_admin_user = mocker.patch(
        'apollo.lib.initialisation.add_admin_user')

    initialise_if_needed()
    add_admin_user.assert_not_called()


def test_add_admin_user(db_session):
    add_admin_user(db_session)

    assert get_user_by_username(
        session=db_session, username='admin') is not None
