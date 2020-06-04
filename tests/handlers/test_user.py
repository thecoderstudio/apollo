def test_post_user_successful(test_client, db_session):
    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': 'testing123'}
    )

    assert response.status_code == 201
    assert response.json()['username'] == 'doejohn'


def test_post_user_short_password(test_client):
    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': '123'},
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == (
        'ensure this value has at least 8 characters'
    )


def test_post_user_duplicate_username(test_client, db_session):
    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': 'testing123'},
    )

    assert response.status_code == 201

    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': 'testing123'},
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == 'username must be unique'
