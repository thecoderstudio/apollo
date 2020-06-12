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
