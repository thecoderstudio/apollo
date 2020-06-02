from functools import wraps

from apollo.models import SessionLocal


def with_db_session(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        session = SessionLocal()
        try:
            return func(session=session, *args, **kwargs)
        finally:
            session.close()

    return wrapped
