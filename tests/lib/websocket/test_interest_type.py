import uuid
from unittest.mock import patch

from apollo.lib.websocket.interest_type import (InterestTypeFunctionHandler,
                                                WebSocketObserverInterestType)
from apollo.models.agent import Agent


def test_interest_type_function_handler_run_agent_listing_function(db_session):
    agent_id = uuid.uuid4()
    agent = Agent(
        id=agent_id,
        name='test'
    )
    db_session.add(agent)
    db_session.commit()

    data = InterestTypeFunctionHandler().run_corresponding_function(
        WebSocketObserverInterestType.AGENT_LISTING
    )
    assert len(data) == 1
    assert data[0] == {
        'id': agent_id,
        'name': 'test',
        'connection_state': 'disconnected',
        'external_ip_address': None,
        'operating_system': None,
        'architecture': None
    }


def test_websocket_observer_interest_type_run_corresponding_function():
    interest_type = WebSocketObserverInterestType.AGENT_LISTING
    with patch('apollo.lib.websocket.interest_type.InterestTypeFunctionHandler'
               + '.run_corresponding_function') as patched_function:
        interest_type.run_corresponding_function()
        patched_function.assert_called_with(interest_type)
