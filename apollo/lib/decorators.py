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


def notify_websockets(connection_type):
    """sends function output to connections with type 'connection_type'"""
    def decorate(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from apollo.lib.websocket.app import AppConnectionManager

            output = await func(*args, **kwargs) if \
                inspect.iscoroutinefunction(func) else func(*args, **kwargs)
            await AppConnectionManager().send_message_to_connections(
                connection_type
            )
            return output
        return wrapper
    return decorate
