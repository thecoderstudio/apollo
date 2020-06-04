def test_post_agent_success(test_client, db_session):
    response = test_client.post(
        '/agent',
        json={'name': 'test'}
    )
    agent = response.json()
    oauth_client = agent['oauth_client']

    assert response.status_code == 201
    assert agent['id'] is not None
    assert oauth_client['agent_id'] is not None
    assert oauth_client['secret'] is not None
    assert oauth_client['type'] == 'confidential'


def test_post_agent_name_exists(test_client, db_session):
    agent = {'name': 'test'}
    test_client.post('/agent', json=agent)
    response = test_client.post('/agent', json=agent)

    assert response.status_code == 422