def test_post_user_successful(test_client, init_test_database):
    response = test_client.post(
        '/token',
        json={'username': 'johndoe', 'password': 'testing123'}
    )

    assert response.status_code == 200
    