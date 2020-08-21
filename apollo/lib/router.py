import copy
import inspect

from fastapi import APIRouter, Depends, Request, WebSocket
from starlette.requests import HTTPConnection
from sqlalchemy.orm import Session

from apollo.lib.security import Allow, AuthorizationPolicy, Everyone
from apollo.lib.signature import copy_parameters
from apollo.models import get_session


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

            @websocket_route(*outer_args, **outer_kwargs)
            async def wrapped(websocket: WebSocket,
                              session: Session = Depends(get_session),
                              *args, **kwargs):
                return await self._call_handler_with_authentication(
                    func, permission, websocket, 'websocket', session, *args,
                    **kwargs
                )

            wrapped_signature = inspect.signature(wrapped)
            func_signature = inspect.signature(func)
            wrapped.__signature__ = copy_parameters(wrapped_signature,
                                                    func_signature,
                                                    ['websocket', 'session'])
            return wrapped
        return decorate

    async def _call_handler_with_authentication(
        self, handler, permission,
        http_connection: HTTPConnection,
        http_connection_type: str,
        session: Session,
        *args, **kwargs
    ):
        enhanced_http_connection = self.acl_policy.enhance_http_connection(
            http_connection, session)
        self.acl_policy.validate_permission(permission,
                                            enhanced_http_connection)
        new_kwargs = self._propagate_kwargs_if_requested(handler, kwargs, {
            'session': session,
            http_connection_type: enhanced_http_connection
        })

        output = handler(*args, **new_kwargs)
        if inspect.iscoroutine(output):
            output = await output

        return output

    @staticmethod
    def _propagate_kwargs_if_requested(func, kwargs, kwargs_for_propagation):
        new_kwargs = copy.copy(kwargs)
        func_signature = inspect.signature(func)
        for kwarg, kwarg_value in kwargs_for_propagation.items():
            if func_signature.parameters.get(kwarg):
                new_kwargs[kwarg] = kwarg_value

        return new_kwargs

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

        @route(*outer_args, **outer_kwargs)
        async def wrapped(request: Request,
                          session: Session = Depends(get_session),
                          *args, **kwargs):
            return await self._call_handler_with_authentication(
                func, permission, request, 'request', session, *args, **kwargs)

        wrapped_signature = inspect.signature(wrapped)
        func_signature = inspect.signature(func)
        wrapped.__signature__ = copy_parameters(wrapped_signature,
                                                func_signature,
                                                ['request', 'session'])
        return wrapped
