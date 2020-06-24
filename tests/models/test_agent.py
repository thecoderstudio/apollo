from fastapi.websockets import WebSocket

from apollo import app
from apollo.lib.websocket_manager import WebSocketManager
from apollo.models.agent import Agent, get_agent_by_name, list_all_agents
from apollo.models.oauth import OAuthClient
from starlette.websockets import WebSocketState


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


def test_agent_connection_status(db_session, test_client):
    agent = Agent(name='test')
    db_session.add(agent)
    db_session.flush()
    agent_id = agent.id
    db_session.commit()

    websocket_manager = WebSocketManager()

    @app.websocket_route('/websocket_connect')
    async def connect(websocket: WebSocket):
        websocket_manager.connections[agent_id] = websocket
        await websocket.accept()
        agent = get_agent_by_name(
            db_session, 'test').connection_status == 'connected'

        websocket.client_state = WebSocketState.CONNECTING
        assert agent.client_state == 'connecting'

        websocket.close()
        assert agent.connection_status == 'disconnected'

        await websocket_manager.close_and_remove_all_connections()
        assert agent.connection_status == 'no connection available'

    test_client.websocket_connect('/websocket_connect')
