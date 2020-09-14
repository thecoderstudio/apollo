from apollo.lib.hash import hash_plaintext
from apollo.models.role import get_role_by_name
from apollo.models.user import User


def test_post_user_successful(test_client, db_session, session_cookie):
    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': 'testing123'},
        cookies=session_cookie
    )

    assert response.status_code == 201
    assert response.json()['username'] == 'doejohn'


def test_post_user_short_password(test_client, session_cookie):
    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': '123'},
        cookies=session_cookie
    )

    assert response.status_code == 400
    assert response.json()['password']['msg'] == (
        'ensure this value has at least 8 characters'
    )


def test_post_user_username_too_long(test_client, session_cookie):
    response = test_client.post(
        '/user',
        json={'username': 'johndoeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
              'password': 'password'},
        cookies=session_cookie
    )

    assert response.status_code == 400
    assert response.json()['username']['msg'] == (
        'ensure this value has at most 36 characters'
    )


def test_post_user_password_contains_whitespace(test_client, session_cookie):
    response = test_client.post(
        '/user',
        json={'username': 'johndoe',
              'password': 'pass word'},
        cookies=session_cookie
    )

    assert response.status_code == 400
    assert response.json()['password']['msg'] == (
        "password can't contain whitespaces"
    )


def test_post_user_username_too_short(test_client, session_cookie):
    response = test_client.post(
        '/user',
        json={'username': 'test', 'password': '123'},
        cookies=session_cookie
    )

    assert response.status_code == 400
    assert response.json()['password']['msg'] == (
        'ensure this value has at least 8 characters'
    )


def test_post_user_duplicate_username(test_client, db_session, session_cookie):
    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': 'testing123'},
        cookies=session_cookie
    )

    assert response.status_code == 201

    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': 'testing123'},
        cookies=session_cookie
    )

    assert response.status_code == 400
    assert response.json()['username']['msg'] == 'username must be unique'


def test_post_user_unauthenticated(test_client, db_session):
    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': 'testing123'}
    )

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."


def test_post_user_as_regular_user(test_client, db_session, user,
                                   session_cookie):
    user.role = None
    db_session.commit()

    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': 'testing123'},
        cookies=session_cookie
    )

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."


def test_update_password_successful(test_client, db_session, session_cookie,
                                    user):
    response = test_client.put(
        f'/user/{user.id}',
        json={'password': 'newpassword', 'old_password': 'testing123'}
    )

    assert response.status_code == 200
    user = db_session.query(User).get(user.id)
    assert user.password_hash == hash_plaintext(
        'newpassword', user.password_salt)


def test_update_password_wrong_password(test_client, db_session, 
                                        session_cookie, user):
    response = test_client.put(
        f'/user/{user.id}',
        json={'password': 'newpassword', 'old_password': 'wrongpassword'}
    )

    assert response.status_code == 403


def test_list_users_unauthenticated(test_client):
    response = test_client.get('/user')

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."


def test_list_users_as_regular_user(test_client, db_session, user,
                                    session_cookie):
    user.role = None
    db_session.commit()

    response = test_client.get('/user', cookies=session_cookie)

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."


def test_list_users_successful(test_client, db_session, session_cookie):
    user_1_id, user_2_id = add_multiple_users(db_session)

    response = test_client.get('/user', cookies=session_cookie)

    users = response.json()
    assert {
        'id': str(user_1_id),
        'username': 'johndoe',
        'role': None,
        'has_changed_initial_password': False 
    } in users
    assert {
        'id': str(user_2_id),
        'username': 'jeffjefferson',
        'role': {
            'name': 'admin'
        },
        'has_changed_initial_password': False
    } in users
    assert response.status_code == 200


def add_multiple_users(db_session):
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
        password_salt='$2b$12$FdTnxaL.NlRdEHREzbU3k.',
        role=get_role_by_name(db_session, 'admin')
    )
    db_session.add(user_1)
    db_session.add(user_2)
    db_session.flush()
    user_1_id = user_1.id
    user_2_id = user_2.id
    db_session.commit()

    return user_1_id, user_2_id


def test_delete_unauthenticated(test_client):
    response = test_client.delete('/user/e670cce4-b36d-4c26-aaae-369d4eba31d3')

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."


def test_delete_as_regular_user(test_client, db_session, user, session_cookie):
    user.role = None
    db_session.commit()

    response = test_client.delete('/user/e670cce4-b36d-4c26-aaae-369d4eba31d3',
                                  cookies=session_cookie)

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."


def test_delete_user_not_found(test_client, session_cookie):
    response = test_client.delete('/user/e670cce4-b36d-4c26-aaae-369d4eba31d3',
                                  cookies=session_cookie)

    assert response.status_code == 404
    assert response.json()['detail'] == "User not found"


def test_delete_admin_user(test_client, db_session, session_cookie):
    _, user_id = add_multiple_users(db_session)

    response = test_client.delete(f"/user/{user_id}", cookies=session_cookie)

    assert response.status_code == 400
    assert response.json()['detail'] == "Can't delete other admins"


def test_delete_successful(test_client, db_session, session_cookie):
    user_id, _ = add_multiple_users(db_session)

    response = test_client.delete(f"/user/{user_id}", cookies=session_cookie)

    assert response.status_code == 204
    assert db_session.query(User).get(user_id) is None

def test_get_current_user_successful(test_client, user, session_cookie):
    response = test_client.get('/user/me', cookies=session_cookie)

    assert response.status_code == 200
    assert response.json() == {
        'id': str(user.id),
        'username': user.username,
        'role': {
            'name': user.role.name
        },
        'has_changed_initial_password': False
    }
