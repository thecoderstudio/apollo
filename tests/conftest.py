import contextlib
from configparser import ConfigParser

from pytest import fixture

import apollo.lib.settings
from apollo.models import Base, init_sqlalchemy, SessionLocal


@fixture
def settings():
    yield apollo.lib.settings.settings
    apollo.lib.settings.settings = {}


@fixture
def db_session():
    try:
        config = ConfigParser()
        config.read('test.ini')
        init_sqlalchemy(config)
        session = SessionLocal()
        yield session
    finally:
        apollo.lib.settings.settings = {}
        empty_tables()
        session.close()


def empty_tables():
    with contextlib.closing(Base.metadata.bind.connect()) as con:
        trans = con.begin()
        for table in reversed(Base.metadata.sorted_tables):
            con.execute(table.delete())
        trans.commit()
