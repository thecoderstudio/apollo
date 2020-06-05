from functools import wraps

from fastapi import APIRouter, Header, WebSocket

from apollo.lib.security import Allow, AuthorizationPolicy, Everyone


class SecureRouter(APIRouter):
    def __init__(self, acl=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.acl = acl
        self.acl_policy = AuthorizationPolicy(self)

    def __acl__(self):
        return self.acl + [(Allow, Everyone, 'public')]

    def websocket(self, *outer_args, permission='public', **outer_kwargs):
        def decorate(func):
            websocket_route = super(SecureRouter, self).websocket
            @wraps(func)
            @websocket_route(*outer_args, **outer_kwargs)
            async def wrapped(websocket: WebSocket, *args, **kwargs):
                self.acl_policy.validate_permission(
                    permission, websocket.headers)
                await func(websocket, *args, **kwargs)
            return wrapped
        return decorate

    def post(self, *outer_args, **outer_kwargs):
        return lambda func: self._http_method(
            func, 'post', *outer_args, **outer_kwargs)

    def put(self, *outer_args, **outer_kwargs):
        return lambda func: self._http_method(
            func, 'put', *outer_args, **outer_kwargs)

    def patch(self, *outer_args, **outer_kwargs):
        return lambda func: self._http_method(
            func, 'patch', *outer_args, **outer_kwargs)

    def delete(self, *outer_args, **outer_kwargs):
        return lambda func: self._http_method(
            func, 'delete', *outer_args, **outer_kwargs)

    def get(self, *outer_args, **outer_kwargs):
        return lambda func: self._http_method(
            func, 'get', *outer_args, **outer_kwargs)

    def options(self, *outer_args, **outer_kwargs):
        return lambda func: self._http_method(
            func, 'options', *outer_args, **outer_kwargs)

    def trace(self, *outer_args, **outer_kwargs):
        return lambda func: self._http_method(
            func, 'trace', *outer_args, **outer_kwargs)

    def head(self, *outer_args, **outer_kwargs):
        return lambda func: self._http_method(
            func, 'head', *outer_args, **outer_kwargs)

    def _http_method(self, func, http_method, *outer_args, permission='public',
                     **outer_kwargs):
        route = getattr(super(SecureRouter, self), http_method)
        @wraps(func)
        @route(*outer_args, **outer_kwargs)
        def wrapped(authorization: str = Header(None), *args, **kwargs):
            self.acl_policy.validate_permission(permission, {
                'authorization': authorization
            })
            return func(*args, **kwargs)
        return wrapped