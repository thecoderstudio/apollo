import uuid
from unittest.mock import Mock

import pytest
from sqlalchemy.orm.session import Session

import apollo.models
from apollo.models import (get_connection_url, get_session, init_sqlalchemy,
                           persist, rollback, commit, save)
from apollo.models.agent import Agent


def test_get_connection_url():
    connection_url = get_connection_url({
        'SQLAlchemy': {
            'driver': 'postgresql',
            'user': 'test',
            'password': 'test',
            'host': 'localhost',
            'database': 'test'
        }
    })

    assert connection_url == "postgresql://test:test@localhost/test"


def test_init_sqlalchemy(monkeypatch):
    monkeypatch.setattr(apollo.models, 'get_connection_url',
                        lambda _: 'sqlite:///:memory:')

    init_sqlalchemy()

    from apollo.models import Base
    assert str(Base.metadata.bind.url) == 'sqlite:///:memory:'


def test_get_session(mocker):
    spy = mocker.spy(Session, 'close')

    session = list(get_session())[0]

    assert session.is_active
    spy.assert_called_once()


def test_persist(db_session):
    agent_id = uuid.uuid4()
    persist(db_session, Agent(id=agent_id, name='test'))
    agent = db_session.query(Agent).get(agent_id)
    assert agent is not None


def test_rollback(db_session):
    agent_id = uuid.uuid4()
    db_session.add(Agent(id=agent_id, name='test'))
    db_session.flush()
    rollback(db_session)
    agent = db_session.query(Agent).get(agent_id)
    assert agent is None


def test_commit(db_session):
    agent_id = uuid.uuid4()
    db_session.add(Agent(id=agent_id, name='test'))
    commit(db_session)
    agent = db_session.query(Agent).get(agent_id)
    assert agent is not None


def test_save_success(db_session):
    agent_copy, agent_id = save(db_session, Agent(name='test'))
    agent = db_session.query(Agent).get(agent_id)
    assert agent_copy.id == agent.id
    assert agent.id == agent_id


def test_save_no_id(mocker, db_session):
    mocker.patch('apollo.models.persist', return_value=Mock(spec=[]))
    agent_copy, agent_id = save(db_session, Agent(name='test'))
    assert agent_id is None


def test_save_rollback(mocker, db_session):
    mocker.patch('apollo.models.persist', side_effect=Exception('test'))
    agent_id = uuid.uuid4()

    with pytest.raises(Exception):
        save(db_session, Agent(id=agent_id, name='test'))

    assert db_session.query(Agent).get(agent_id) is None
