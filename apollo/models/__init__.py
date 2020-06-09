import copy
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from apollo.lib.settings import settings

log = logging.getLogger(__name__)

SessionLocal = sessionmaker(autocommit=False, autoflush=False)
Base = declarative_base()

log = logging.getLogger(__name__)


def init_sqlalchemy(settings_=settings):
    engine = create_engine(get_connection_url(settings_))
    SessionLocal.configure(bind=engine)
    Base.metadata.bind = engine
    return engine


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


def persist(session, obj):
    log.debug("persisting object %r", obj)
    session.add(obj)
    session.flush()
    return obj


def rollback(session):
    log.debug("Rolling back session: %r", session.dirty)
    return session.rollback()


def commit(session):
    log.debug("Committing session: %r", session.dirty)
    session.commit()


def save(session, obj):
    try:
        obj = persist(session, obj)
        try:
            id_ = obj.id
        except AttributeError:
            id_ = None
        # Shallow copy to be able to return generated data without having
        # to request the object again to get it in session.
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

    return obj_copy, id_
