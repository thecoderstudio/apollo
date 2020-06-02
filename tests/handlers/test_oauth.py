def test_post_access_token_success(test_client, db_session):
    response = test_client.post('/oauth/token')

    assert response.status_code == 201
