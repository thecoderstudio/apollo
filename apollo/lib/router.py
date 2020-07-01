import inspect
from functools import wraps

from fastapi import APIRouter, Request, WebSocket

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
                self.acl_policy.validate_permission(permission, websocket)
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
        wrapped = self._get_wrapped(
            func, route, permission, *outer_args, **outer_kwargs)

        wrapped_signature = inspect.signature(wrapped)
        func_signature = inspect.signature(func)
        func_parameters = [func_signature.parameters[key] for key in
                           func_signature.parameters]

        new_parameters = (
            [wrapped_signature.parameters['request']] + func_parameters)
        new_signature = func_signature.replace(parameters=new_parameters)

        wrapped.__signature__ = new_signature
        return wrapped

    def _get_wrapped(self, func, route, permission,
                     *outer_args, **outer_kwargs):
        if inspect.iscoroutinefunction(func):
            @route(*outer_args, **outer_kwargs)
            async def wrapped(request: Request, *args, **kwargs):
                self.acl_policy.validate_permission(permission, request)
                return await func(*args, **kwargs)
        else:
            @route(*outer_args, **outer_kwargs)
            def wrapped(request: Request, *args, **kwargs):
                self.acl_policy.validate_permission(permission, request)
                return func(*args, **kwargs)

        return wrapped
