import apollo.models
from apollo.models import get_connection_url, get_session, init_sqlalchemy

from sqlalchemy.orm.session import Session


# def test_get_connection_url():
#     connection_url = get_connection_url({
#         'SQLAlchemy': {
#             'driver': 'postgresql',
#             'user': 'test',
#             'password': 'test',
#             'host': 'localhost',
#             'database': 'test'
#         }
#     })

#     assert connection_url == "postgresql://test:test@localhost/test"


# def test_init_sqlalchemy(monkeypatch):
#     monkeypatch.setattr(apollo.models, 'get_connection_url',
#                         lambda _: 'sqlite:///:memory:')

#     init_sqlalchemy()

#     from apollo.models import Base
#     assert str(Base.metadata.bind.url) == 'sqlite:///:memory:'


# def test_get_session(mocker):
#     spy = mocker.spy(Session, 'close')

#     session = list(get_session())[0]

#     assert session.is_active
#     spy.assert_called_once()
