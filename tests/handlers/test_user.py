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

    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == (
        'ensure this value has at least 8 characters'
    )


def test_post_user_username_too_long(test_client, session_cookie):
    response = test_client.post(
        '/user',
        json={'username': 'johndoeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
              'password': 'password'},
        cookies=session_cookie
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == (
        'ensure this value has at most 36 characters'
    )


def test_post_user_password_contains_whitespace(test_client, session_cookie):
    response = test_client.post(
        '/user',
        json={'username': 'johndoe',
              'password': 'pass word'},
        cookies=session_cookie
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == (
        "password can't contain whitespaces"
    )


def test_post_user_username_too_short(test_client, session_cookie):
    response = test_client.post(
        '/user',
        json={'username': 'test', 'password': '123'},
        cookies=session_cookie
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == (
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

    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == 'username must be unique'
