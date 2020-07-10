import inspect
from functools import wraps
from unittest.mock import patch


def assert_interested_connections_messaged(interest_type):
    def decorate(func):
        if not inspect.iscoroutinefunction(func):
            raise ValueError(
                "func has to be a coroutine to use this decorator"
            )

        @wraps(func)
        async def wrapped(*args, **kwargs):
            with patch(
                "apollo.lib.websocket.app.AppConnectionManager."
                "message_interested_connections"
            ) as message_interested_connections:
                output = await func(*args, **kwargs)

                message_interested_connections.assert_called_with(
                    interest_type)

            return output
        return wrapped
    return decorate
