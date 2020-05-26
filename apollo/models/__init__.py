from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from apollo.lib.settings import settings

SessionLocal = sessionmaker(autocommit=False, autoflush=False)
Base = declarative_base()


def init_sqlalchemy():
    engine = create_engine(get_connection_url(settings), connect_args={
        'check_same_thread': False
    })
    SessionLocal.configure(bind=engine)
    Base.metadata.bind = engine


def get_connection_url(settings_):
    return "{driver}://{user}:{password}@{host}/{database}".format(
        **settings['sqlalchemy']
    )


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
