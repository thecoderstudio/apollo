import copy
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from apollo.lib.settings import settings

log = logging.getLogger(__name__)

SessionLocal = sessionmaker(autocommit=False, autoflush=False)
Base = declarative_base()


def init_sqlalchemy():

    print("**" * 100)
    engine = create_engine(get_connection_url(settings))
    SessionLocal.configure(bind=engine)
    Base.metadata.bind = engine


def get_connection_url(settings_):
    return "{driver}://{user}:{password}@{host}/{database}".format(
        **settings_['SQLAlchemy']
    )


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def commit(session):
    log.info("Committing session: %r", session.dirty)
    session.commit()


def persist(obj, session):
    log.debug("persisting object %r", obj)
    session.add(obj)
    session.flush()
    return obj


def rollback(session):
    log.debug("Rolling back session: %r", session.dirty)
    return session.rollback()


def save(obj):
    try:
        session = SessionLocal()
        obj = persist(obj, session)
        obj_copy = copy.copy(obj)
    except Exception as e:
        log.critical(
            'Something went wrong saving the {}'.format(
                obj.__class__.__name__),
            exc_info=True)
        rollback(session)
        raise e
    finally:
        commit(session)
        session.close()

    return obj_copy
