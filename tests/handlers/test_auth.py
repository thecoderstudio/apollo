import pytest

from apollo.lib.hash import hash_plaintext
from apollo.models.user import User


def test_login_success(test_client, db_session):
    username, password = create_test_user(db_session)
    response = test_client.post('/auth/login', json={
        'username': username,
        'password': password
    })

    assert response.status_code == 200
    assert response.cookies['session'] is not None


@pytest.mark.parametrize("username,password", [
    ['testuser', 'fakepassword'],
    ['fakeuser', 'testing123']
])
def test_login_wrong_credentials(test_client, db_session, username, password):
    create_test_user(db_session)
    response = test_client.post('/auth/login', json={
        'username': username,
        'password': password
    })

    assert response.status_code == 400
    assert response.json()['detail'] == "Username and/or password is incorrect"


def test_locked_after_too_many_attempts(test_client, db_session):
    create_test_user(db_session)
    credentials = {'username': 'testuser', 'password': 'fake123'}
    test_client.post('/auth/login', json=credentials)
    test_client.post('/auth/login', json=credentials)
    test_client.post('/auth/login', json=credentials)
    response = test_client.post('/auth/login', json=credentials)

    assert response.status_code == 400
    assert response.json()['detail'] == (
        "This account is locked, try again in 600 seconds")


def create_test_user(db_session):
    username = 'testuser'
    password = 'testing123'
    password_hash, password_salt = hash_plaintext(password)

    db_session.add(User(
        username=username,
        password_hash=password_hash,
        password_salt=password_salt
    ))
    db_session.commit()
    return (username, password)
