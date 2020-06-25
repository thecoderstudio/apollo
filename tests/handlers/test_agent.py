import uuid

from apollo.models.agent import Agent
from apollo.models.oauth import OAuthClient


def test_post_agent_success(test_client, session_cookie):
    response = test_client.post(
        '/agent',
        json={'name': 'test'},
        cookies=session_cookie
    )
    agent = response.json()
    oauth_client = agent['oauth_client']

    assert response.status_code == 201
    assert agent['id'] is not None
    assert oauth_client['agent_id'] is not None
    assert oauth_client['secret'] is not None
    assert oauth_client['type'] == 'confidential'


def test_post_agent_name_exists(test_client, session_cookie):
    agent = {'name': 'test'}
    test_client.post('/agent', json=agent, cookies=session_cookie)
    response = test_client.post('/agent', json=agent)

    assert response.status_code == 400


def test_post_agent_unauthenticated(test_client, db_session):
    response = test_client.post(
        '/agent',
        json={'name': 'test'}
    )

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."


def test_list_agent_empty_list(db_session, test_client, session_cookie):
    response = test_client.get('/agent', cookies=session_cookie)

    assert response.json() == []


def test_list_agent_success(db_session, test_client, session_cookie):
    agent_id_1 = uuid.uuid4()
    agent_id_2 = uuid.uuid4()
    agent = Agent(id=agent_id_1, name='test',
                  oauth_client=OAuthClient(type='confidential'))
    agent_2 = Agent(id=agent_id_2, name='test2',
                    oauth_client=OAuthClient(type='confidential'))
    db_session.add(agent)
    db_session.add(agent_2)
    db_session.commit()

    response = test_client.get('/agent', cookies=session_cookie)

    assert response.status_code == 200
    response_body = response.json()
    assert len(response_body) == 2

    assert response_body[0]['name'] in ['test', 'test2']
    assert response_body[0]['id'] in [str(agent_id_1), str(agent_id_2)]


def test_list_agent_unauthenticated(test_client):
    response = test_client.get('/agent')

    assert response.status_code == 403
    assert response.json()['detail'] == "Permission denied."
