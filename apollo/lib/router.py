import copy
import inspect
from functools import wraps

from fastapi import APIRouter, Depends, Request, WebSocket
from sqlalchemy.orm import Session

from apollo.lib.security import Allow, AuthorizationPolicy, Everyone
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

            @wraps(func)
            @websocket_route(*outer_args, **outer_kwargs)
            async def wrapped(websocket: WebSocket, *args, **kwargs):
                self.acl_policy.add_http_connection_metadata(websocket)
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
        func_signature = inspect.signature(func)

        @route(*outer_args, **outer_kwargs)
        async def wrapped(request: Request,
                          session: Session = Depends(get_session),
                          *args, **kwargs):
            self.acl_policy.add_http_connection_metadata(request, session)
            self.acl_policy.validate_permission(permission, request)
            if func_signature.parameters.get('request'):
                kwargs['request'] = request
            if func_signature.parameters.get('session'):
                kwargs['session'] = session
            output = func(*args, **kwargs)
            if inspect.iscoroutine(output):
                output = await output

            return output

        wrapped_signature = inspect.signature(wrapped)
        func_parameters = [
            func_signature.parameters[key] for key in
            func_signature.parameters if key not in ['request', 'session']]

        new_parameters = self.bulk_create_new_parameters(
            func_parameters, [
                wrapped_signature.parameters['session'],
                wrapped_signature.parameters['request']
            ]
        )
        new_signature = func_signature.replace(parameters=new_parameters)

        wrapped.__signature__ = new_signature
        return wrapped

    def bulk_create_new_parameters(self, existing_parameters, new_parameters):
        parameters = existing_parameters
        for new_parameter in new_parameters:
            parameters = self.create_new_parameters(parameters, new_parameter)
        return parameters

    def create_new_parameters(self, existing_parameters, new_parameter):
        if not existing_parameters:
            return [new_parameter]

        if self.check_parameter_has_default(new_parameter):
            new_parameters = copy.copy(existing_parameters)
            for i, parameter in enumerate(new_parameters):
                if self.check_parameter_has_default(parameter):
                    new_parameters.insert(i, new_parameter)
                    return new_parameters

                return existing_parameters + [new_parameter]
        else:
            return [new_parameter] + existing_parameters

    def check_parameter_has_default(self, parameter):
        return parameter.default != inspect.Parameter.empty
