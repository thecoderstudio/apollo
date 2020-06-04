from functools import wraps

from fastapi import APIRouter, WebSocket

from apollo.lib.security import Allow, AuthorizationPolicy, Everyone


class SecureRouter(APIRouter):
    def __init__(self, acl=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.acl = acl
        self.acl_policy = AuthorizationPolicy(self)

    def __acl__(self):
        return self.acl + [(Allow, Everyone, 'public')]

    def websocket_(self, *outer_args, permission='public', **outer_kwargs):
        def decorate(func):
            @wraps(func)
            @self.websocket(*outer_args, **outer_kwargs)
            async def wrapped(websocket: WebSocket, *args, **kwargs):
                self.acl_policy.validate_permission(
                    permission, websocket.headers)
                await func(websocket, *args, **kwargs)
            return wrapped
        return decorate
