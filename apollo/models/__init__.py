import copy
import logging
from functools import wraps

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


def _delete(session, obj):
    log.debug(f"deleting object {obj}")
    session.delete(obj)


def rollback(session):
    log.debug("Rolling back session: %r", session.dirty)
    return session.rollback()


def commit(session):
    log.debug("Committing session: %r", session.dirty)
    session.commit()


def rollback_on_failure(action):
    def decorate(func):
        @wraps(func)
        def wrapped(session, obj, *args, **kwargs):
            try:
                return func(session, obj, *args, **kwargs)
            except Exception as e:
                log.critical(
                    "Something went wrong {} the {}".format(
                        action, obj.__class__.__name__),
                    exc_info=True
                )
                rollback(session)
                raise e
            finally:
                commit(session)
        return wrapped
    return decorate


@rollback_on_failure('saving')
def save(session, obj):
    obj = persist(session, obj)
    try:
        id_ = obj.id
    except AttributeError:
        id_ = None
    # Shallow copy to be able to return generated data without having
    # to request the object again to get it in session.
    obj_copy = copy.copy(obj)

    return obj_copy, id_


@rollback_on_failure('deleting')
def delete(session, obj):
    _delete(session, obj)
