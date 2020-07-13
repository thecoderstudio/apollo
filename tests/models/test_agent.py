import pytest
from starlette.websockets import WebSocketState

from apollo.lib.websocket.agent import AgentConnection
from apollo.models.agent import Agent, get_agent_by_name, list_all_agents
from apollo.models.oauth import OAuthClient


def test_agent_cascades(db_session):
    agent = Agent(
        name='test',
        oauth_client=OAuthClient(
            type='confidential'
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


def test_get_agent_by_name(db_session):
    agent = Agent(name='test')
    db_session.add(agent)
    db_session.flush()
    agent_id = agent.id
    db_session.commit()

    persisted_agent = get_agent_by_name(db_session, 'test')
    assert persisted_agent.id == agent_id


def test_get_agent_by_name_not_found(db_session):
    agent = Agent(name='test')
    db_session.add(agent)
    db_session.commit()

    assert get_agent_by_name(db_session, 'different') is None


def test_list_all_agents_size(db_session):
    db_session.add(Agent(name='test'))
    db_session.commit()

    assert len(list_all_agents(db_session)) == 1

    db_session.add(Agent(name='test2'))
    db_session.commit()

    assert len(list_all_agents(db_session)) == 2


@pytest.mark.asyncio
async def test_agent_connection_status(
    db_session, mocker, websocket_mock, agent_connection_manager
):
    agent = Agent(name='test')
    db_session.add(agent)
    db_session.flush()
    agent_id = agent.id
    db_session.commit()

    agent_connection = AgentConnection(websocket_mock, agent_id)
    await agent_connection_manager._accept_connection(agent_connection)

    agent = get_agent_by_name(db_session, 'test')
    assert agent.connection_state == WebSocketState.CONNECTED

    agent_connection.client_state = WebSocketState.CONNECTING
    assert agent.connection_state == WebSocketState.CONNECTING

    agent_connection.client_state = WebSocketState.DISCONNECTED
    assert agent_connection.client_state == WebSocketState.DISCONNECTED
