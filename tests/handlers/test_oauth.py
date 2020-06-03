import base64
import uuid
from secrets import token_hex

from apollo.models.agent import Agent
from apollo.models.oauth import OAuthClient


def test_post_access_token_success(test_client, db_session):
    encoded_creds = get_encoded_creds(*persist_test_agent(db_session))
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


def test_post_access_token_invalid_grant_type(test_client):
    response = test_client.post(
        '/oauth/token',
        json={
            'grant_type': 'test'
        }
    )

    assert response.status_code == 422


def test_post_access_token_client_not_authorized(mocker, test_client,
                                                 db_session):
    encoded_creds = get_encoded_creds(*persist_test_agent(db_session))
    mocked = mocker.patch('apollo.handlers.oauth.get_client')
    mocked.client_type = 'test'
    response = test_client.post(
        '/oauth/token',
        headers={
            'Authorization': f"Basic {encoded_creds}"
        },
        json={
            'grant_type': 'client_credentials'
        }
    )

    assert response.status_code == 400
    assert response.json() == {
        'detail': "Client not authorized to use this grant type"
    }


def test_post_access_token_invalid_auth_method(test_client, db_session):
    encoded_creds = get_encoded_creds(*persist_test_agent(db_session))
    response = test_client.post(
        '/oauth/token',
        headers={
            'Authorization': f"Bearer {encoded_creds}"
        },
        json={
            'grant_type': 'client_credentials'
        }
    )

    assert response.status_code == 400
    assert "Wrong authorization method" in response.json()['detail']


def test_post_access_token_invalid_auth_header(test_client):
    malformed_creds = base64.b64encode(b"test value").decode('utf-8')
    response = test_client.post(
        '/oauth/token',
        headers={
            'Authorization': f"Basic {malformed_creds}"
        },
        json={
            'grant_type': 'client_credentials'
        }
    )

    assert response.status_code == 400
    assert "Invalid authorization header" in response.json()['detail']


def test_post_access_token_no_client_found(test_client, db_session):
    fake_creds = base64.b64encode(
        f"{uuid.uuid4()}:{token_hex(32)}".encode('utf-8')
    ).decode('utf-8')
    response = test_client.post(
        '/oauth/token',
        headers={
            'Authorization': f"Basic {fake_creds}"
        },
        json={
            'grant_type': 'client_credentials'
        }
    )

    assert response.status_code == 400
    assert response.json() == {
        'detail': "No client found for given client_id"
    }


def persist_test_agent(db_session):
    agent = Agent(
        name='test',
        oauth_client=OAuthClient(client_type='confidential')
    )
    db_session.add(agent)
    db_session.flush()

    agent_id = agent.id
    client_secret = agent.oauth_client.client_secret

    db_session.commit()

    return agent_id, client_secret


def get_encoded_creds(agent_id, client_secret):
    creds = f"{agent_id}:{client_secret}"
    return base64.b64encode(creds.encode('utf-8')).decode('utf-8')
