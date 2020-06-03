def test_post_user_successful(test_client, db_session):
    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': 'testing123'}
    )

    assert response.status_code == 200
    assert response.json()['username'] == 'doejohn'

    
def test_post_user_short_password(test_client, db_session):
    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': '123'},
    )

    assert response.status_code == 422

def test_post_user_duplicate_username(test_client, db_session):
    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': 'testing123'},
    )

    assert response.status_code == 200

    response = test_client.post(
        '/user',
        json={'username': 'doejohn', 'password': 'testing123'},
    )

    assert response.status_code == 422