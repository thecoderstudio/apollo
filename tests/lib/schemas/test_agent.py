import pytest
from pydantic import ValidationError

from apollo.lib.schemas.agent import CreateAgentSchema
from apollo.models.agent import Agent


def test_create_agent_valid(db_session):
    agent = CreateAgentSchema(name="Test Name ")
    assert agent.name == "Test Name"


def test_create_agent_name_exists(db_session):
    db_session.add(Agent(name='test'))
    db_session.commit()
    with pytest.raises(ValueError,
                       match="An agent with the given name already exists"):
        CreateAgentSchema(name='test')


def test_create_agent_empty_name():
    with pytest.raises(ValidationError, match="at least 1 characters"):
        CreateAgentSchema(name='')


def test_create_agent_name_too_long(db_session):
    with pytest.raises(ValidationError, match="at most 100 characters"):
        CreateAgentSchema(name=''.join(["a" for i in range(101)]))
    CreateAgentSchema(name=''.join(["a" for i in range(100)]))
