import pytest
from fastapi import WebSocket
from starlette.websockets import WebSocketState

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
async def test_agent_connection_status(db_session, mocker, websocket_manager):
    agent = Agent(name='test')
    db_session.add(agent)
    db_session.flush()
    agent_id = agent.id
    db_session.commit()

    websocket_mock = mocker.create_autospec(WebSocket)
    await websocket_manager.connect_agent(agent_id, websocket_mock)

    websocket_mock.client_state = WebSocketState.CONNECTED
    agent = get_agent_by_name(db_session, 'test')
    assert agent.connection_state == WebSocketState.CONNECTED

    websocket_mock.client_state = WebSocketState.CONNECTING
    assert agent.connection_state == WebSocketState.CONNECTING

    await websocket_manager.close_agent_connection(agent_id)
    assert agent.connection_state == WebSocketState.DISCONNECTED
