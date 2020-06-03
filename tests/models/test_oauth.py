import datetime
import uuid
from secrets import token_hex

import pytest
from sqlalchemy.orm.exc import NoResultFound

from apollo.models.agent import Agent
from apollo.models.oauth import (OAuthAccessToken, OAuthClient,
                                 get_client_by_creds)


def test_oauth_access_token_expired():
    expired_token = OAuthAccessToken(
        expiry_date=datetime.datetime.now(datetime.timezone.utc)
    )
    unexpired_token = OAuthAccessToken(
        expiry_date=datetime.datetime.now(datetime.timezone.utc) +
        datetime.timedelta(hours=1)
    )

    assert expired_token.expired
    assert not unexpired_token.expired


def test_oauth_client_cascades(db_session):
    agent = Agent(
        name='test',
        oauth_client=OAuthClient(
            client_type='confidential',
            tokens=[
                OAuthAccessToken(
                    expiry_date=datetime.datetime.now(datetime.timezone.utc)
                ),
                OAuthAccessToken(
                    expiry_date=datetime.datetime.now(datetime.timezone.utc)
                )
            ]
        )
    )
    db_session.add(agent)
    db_session.flush()
    agent_id = agent.id
    db_session.commit()

    persisted_agent = db_session.query(Agent).get(agent_id)
    db_session.delete(persisted_agent.oauth_client)
    db_session.commit()

    assert len(db_session.query(OAuthAccessToken).all()) == 0
    assert len(db_session.query(OAuthClient).all()) == 0
    assert db_session.query(Agent).get(agent_id) is not None


def test_get_client_by_creds(db_session):
    agent = Agent(
        name='test',
        oauth_client=OAuthClient(client_type='confidential')
    )
    db_session.add(agent)
    db_session.flush()
    agent_id = agent.id
    client_secret = agent.oauth_client.client_secret
    db_session.commit()

    client = get_client_by_creds(db_session, agent_id, client_secret)
    assert client.agent_id == agent_id


def test_get_client_by_creds_not_found(db_session):
    with pytest.raises(NoResultFound):
        get_client_by_creds(db_session, uuid.uuid4(), token_hex(32))
