import datetime

from apollo.models.agent import Agent
from apollo.models.oauth import OAuthAccessToken, OAuthClient


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
