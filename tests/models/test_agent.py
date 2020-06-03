from apollo.models.agent import Agent
from apollo.models.oauth import OAuthClient


def test_agent_cascades(db_session):
    agent = Agent(
        name='test',
        oauth_client=OAuthClient(
            client_type='confidential'
        )
    )
    db_session.add(agent)
    db_session.flush()
    agent_id = agent.id
    db_session.commit()

    persisted_agent = db_session.query(Agent).get(agent_id)
    db_session.delete(persisted_agent)
    db_session.commit()

    assert len(db_session.query(OAuthClient).all()) == 0
