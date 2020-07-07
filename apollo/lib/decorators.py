import inspect
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


def notify_websockets(observer_interest_type):
    """sends function output to connections with type 'interest_type'"""
    def decorate(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from apollo.lib.websocket.app import AppConnectionManager

            output = func(*args, **kwargs)
            if inspect.iscoroutine(output):
                output = await output

            await AppConnectionManager().send_message_to_connections(
                observer_interest_type
            )
            return output
        return wrapper
    return decorate
