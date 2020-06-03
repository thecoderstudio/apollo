def test_post_user_successful(test_client):
    response = test_client.post(
        '/token',
        json={'username': 'johndoe', 'password': 'testing123'}
    )

    assert response.status_code == 200