def test_post_agent_success(test_client, db_session):
    response = test_client.post(
        '/agent',
        json={'name': 'test'}
    )

    assert response.status_code == 201


def test_post_agent_name_exists(test_client, db_session):
    agent = {'name': 'test'}
    test_client.post('/agent', json=agent)
    response = test_client.post('/agent', json=agent)

    assert response.status_code == 422
