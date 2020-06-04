from functools import wraps

from fastapi import APIRouter, WebSocket


class Router(APIRouter):
    def websocket_(self, *outer_args, permission='public', **outer_kwargs):
        def decorate(func):
            @wraps(func)
            @self.websocket(*outer_args, **outer_kwargs)
            async def wrapped(websocket: WebSocket, *args, **kwargs):
                await func(websocket, *args, **kwargs)
            return wrapped
        return decorate
