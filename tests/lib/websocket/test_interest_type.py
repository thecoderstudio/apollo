from apollo.lib.websocket.interest_type import WebSocketObserverInterestType
from apollo.models.agent import Agent


def test_websocket_observer_interest_list_all_agents(db_session):
    agent = Agent(name='test')
    db_session.add(agent)
    db_session.commit()

    data = WebSocketObserverInterestType._list_all_agents()
    assert len(data) == 1
    assert data[0]['connection_state'] == 'disconnected'
