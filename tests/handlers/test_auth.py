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


def test_login_wrong_credentials(test_client, db_session, username, password):
    create_test_user(db_session)
    response = test_client.post('/auth/login', json={
        'username': username,
        'password': password
    })


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
