from apollo.lib.hash import hash_plaintext
from apollo.models.user import User


def test_login_success(test_client, db_session):
    username = 'testuser'
    password = 'testing123'
    password_hash, password_salt = hash_plaintext(password)

    db_session.add(User(
        username=username,
        password_hash=password_hash,
        password_salt=password_salt
    ))
    db_session.commit()

    response = test_client.post('/auth/login', json={
        'username': username,
        'password': password
    })

    assert response.status_code == 200
    assert response.cookies['session'] is not None
