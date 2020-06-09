import pytest
from sqlalchemy.orm.exc import NoResultFound

from apollo.models.role import get_role_by_name, Role


def test_get_role_by_name(db_session):
    role = Role(name='test')
    db_session.add(role)
    db_session.flush()
    role_id = role.id
    db_session.commit()

    assert get_role_by_name(db_session, 'test').id == role_id


def test_get_role_by_name_not_found(db_session):
    role = Role(name='test')
    db_session.add(role)
    db_session.commit()

    with pytest.raises(NoResultFound):
        get_role_by_name(db_session, 'different')
