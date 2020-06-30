from functools import wraps
from typing import Callable

from apollo.models import SessionLocal
from apollo.lib.websocket.agent import AppWebSocketConnectionType
from apollo.lib.websocket.app import AppConnectionManager


def with_db_session(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        session = SessionLocal()
        try:
            return func(session=session, *args, **kwargs)
        finally:
            session.close()
    return wrapped


def notify_websockets(connection_type: AppWebSocketConnectionType,
                      function: Callable):
    """sends function output to connections with type 'connection_type'"""

    def decorate(func):
        def wrapper(*args, **kwargs):
            output = function_to_decorate(*args, **kw)

            result = function()
            AppConnectionManager().send_message_to_connections(
                connection_type
            )
            return output
        return wrapper
