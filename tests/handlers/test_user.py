from apollo.lib.hash import compare_plaintext_to_hash
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
        "field can't contain whitespaces"
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


def _assert_successful_update_password(user, response, db_session):
    assert response.status_code == 200
    user = db_session.query(User).get(user.id)
    assert compare_plaintext_to_hash(
        'newpassword', user.password_hash, user.password_salt) is True


def test_update_user_successful_authenticated(test_client, db_session,
                                              session_cookie, user):
    response = test_client.patch(
        '/user/me',
        json={'password': 'newpassword', 'password_confirm': 'newpassword',
              'old_password': 'testing123', 'username': 'newusername'},
        cookies=session_cookie
    )

    _assert_successful_update_password(user, response, db_session)
    assert db_session.query(User).get(user.id).username == 'newusername'


def test_update_password_successful_uninitialized(
    test_client, db_session, session_cookie_for_uninitialized_user,
    uninitialized_user
):
    response = test_client.patch(
        '/user/me',
        json={'password': 'newpassword', 'password_confirm': 'newpassword',
              'old_password': 'testing123'},
        cookies=session_cookie_for_uninitialized_user
    )

    _assert_successful_update_password(uninitialized_user,
                                       response, db_session)


def test_update_password_wrong_password(test_client, db_session,
                                        session_cookie, user):
    response = test_client.patch(
        '/user/me',
        json={'password': 'newpassword', 'old_password': 'wrongpassword',
              'password_confirm': 'newpassword'},
        cookies=session_cookie
    )

    assert response.status_code == 400
    assert response.json()['old_password']['msg'] == 'Invalid password'


def test_update_user_unauthenticated(test_client, user):
    response = test_client.patch(
        '/user/me',
        json={'password': 'newpassword', 'password_confirm': 'newpassword',
              'old_password': 'testing123'}
    )

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."


def test_update_user_password_mismatch(test_client, user, session_cookie):
    response = test_client.patch(
        '/user/me',
        json={'password': 'newpassword', 'password_confirm': 'nepassword',
              'old_password': 'testing123'},
        cookies=session_cookie
    )

    assert response.status_code == 400
    assert response.json()['password_confirm']['msg'] == "passwords must match"


def test_update_user_password_same_as_old_password(test_client, user,
                                                   session_cookie):
    response = test_client.patch(
        '/user/me',
        json={'password': 'testing123', 'password_confirm': 'testing123',
              'old_password': 'testing123'},
        cookies=session_cookie
    )

    assert response.status_code == 400
    assert response.json()['password']['msg'] == (
        "password cannot match old password")


def test_update_user_username_too_long(test_client, session_cookie):
    response = test_client.patch(
        '/user/me',
        json={'username': 'johndoeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'},
        cookies=session_cookie
    )

    assert response.status_code == 400
    assert response.json()['username']['msg'] == (
        'ensure this value has at most 36 characters'
    )


def test_update_user_username_too_short(test_client, session_cookie):
    response = test_client.patch(
        '/user/me',
        json={'username': ''},
        cookies=session_cookie
    )

    assert response.status_code == 400
    assert response.json()['username']['msg'] == (
        'ensure this value has at least 1 characters'
    )


def test_update_user_username_contains_whitespace(test_client, session_cookie):
    response = test_client.patch(
        '/user/me',
        json={'username': 'john doe'},
        cookies=session_cookie
    )

    assert response.status_code == 400
    assert response.json()['username']['msg'] == (
        "field can't contain whitespaces"
    )


def test_update_user_duplicate_username(
        test_client, db_session, session_cookie, user):
    response = test_client.patch(
        '/user/me',
        json={'username': 'test_admin'},
        cookies=session_cookie
    )

    assert response.status_code == 400
    assert response.json()['username']['msg'] == 'username must be unique'


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


def _assert_get_current_user_successful(response, user,
                                        has_changed_initial_password):
    assert response.status_code == 200
    assert response.json() == {
        'id': str(user.id),
        'username': user.username,
        'role': {
            'name': user.role.name
        },
        'has_changed_initial_password': has_changed_initial_password
    }


def test_get_current_user_successful(test_client, user, session_cookie):
    response = test_client.get('/user/me', cookies=session_cookie)
    _assert_get_current_user_successful(response, user, True)


def test_get_current_user_successful_uninitialised(
    test_client, uninitialized_user,
    session_cookie_for_uninitialized_user
):
    response = test_client.get('/user/me',
                               cookies=session_cookie_for_uninitialized_user)
    _assert_get_current_user_successful(response,
                                        uninitialized_user, False)
