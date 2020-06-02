def test_post_access_token_no_auth_header(test_client, db_session):
    response = test_client.post('/oauth/token')

    assert response.status_code == 400
    assert response.json() == {'detail': "No authorization header found"}
