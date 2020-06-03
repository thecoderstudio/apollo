import base64

from apollo.models.agent import Agent
from apollo.models.oauth import OAuthClient


def test_post_access_token_success(test_client, db_session):
    agent = Agent(
        name='test',
        oauth_client=OAuthClient(client_type='confidential')
    )
    db_session.add(agent)
    db_session.flush()

    agent_id = agent.id
    client_secret = agent.oauth_client.client_secret

    db_session.commit()

    creds = f"{agent_id}:{client_secret}"
    encoded_creds = base64.b64encode(creds.encode('utf-8')).decode('utf-8')

    response = test_client.post(
        '/oauth/token',
        headers={
            'Authorization': f"Basic {encoded_creds}"
        },
        json={
            'grant_type': 'client_credentials'
        }
    )
    body = response.json()

    assert response.status_code == 201
    assert body['token_type'] == 'Bearer'
    assert 'access_token' in body
    assert 'expires_in' in body


def test_post_access_token_no_auth_header(test_client, db_session):
    response = test_client.post('/oauth/token', json={
        'grant_type': 'client_credentials'
    })

    assert response.status_code == 400
    assert response.json() == {'detail': "No authorization header found"}
