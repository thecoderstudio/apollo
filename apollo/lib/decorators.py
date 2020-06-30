from functools import wraps
from typing import Callable

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
        def wrapper(*args, **kwargs):
            from apollo.lib.websocket.app import AppConnectionManager
            output = function_to_decorate(*args, **kw)

            result = function()
            AppConnectionManager().send_message_to_connections(
                connection_type
            )
            return output
        return wrapper
    return decorate
