import base64
import logging

import jwt
from fastapi import Depends
from fastapi.security import APIKeyCookie
from sqlalchemy.orm.exc import NoResultFound

from apollo.lib.decorators import with_db_session
from apollo.lib.exceptions import HTTPException
from apollo.lib.exceptions.oauth import (
    AuthorizationHeaderNotFound, InvalidAuthorizationMethod,
    InvalidAuthorizationHeader)
from apollo.lib.settings import settings
from apollo.models import SessionLocal
from apollo.models.oauth import get_access_token_by_token
from apollo.models.user import get_user_by_id

log = logging.getLogger(__name__)

session_cookie = APIKeyCookie(name='session')

Authenticated = 'Authenticated'
Allow = 'Allow'
Agent = 'Agent'
Deny = 'Deny'
Everyone = 'Everyone'
Human = 'Human'


class AuthorizationPolicy:
    def __init__(self, acl_provider):
        self.acl_provider = acl_provider

    def get_principals(self, headers):
        principals = [Everyone]

        access_token = self._get_authenticated_access_token(headers)
        if access_token:
            principals += [Authenticated, Agent,
                           f"agent:{access_token.client.agent_id}"]

        authenticated_user = self._get_current_user()
        if authenticated_user:
            principals += [Authenticated, Human,
                           f"user:{authenticated_user.id}"]

        return principals

    @staticmethod
    @with_db_session
    def _get_authenticated_access_token(headers, session):
        try:
            auth_method, token_string = headers['authorization'].split(' ')
        except (KeyError, AttributeError, ValueError):
            return

        if auth_method != 'Bearer':
            return

        try:
            access_token = get_access_token_by_token(session, token_string)
        except NoResultFound:
            return
        if not access_token.client.active or access_token.expired:
            return

        return access_token

    @staticmethod
    @with_db_session
    def _get_current_user(session: SessionLocal,
                          session_cookie: str = Depends(session_cookie)):
        payload = jwt.decode(session_cookie, settings['session']['secret'])
        return get_user_by_id(session, payload['authenticated_user_id'])

    def get_complete_acl(self, context_acl_provider=None):
        acl = self.acl_provider.__acl__()
        if not context_acl_provider:
            return acl

        return context_acl_provider.__acl__() + acl

    def check_permission(self, requested_permission,
                         headers, context_acl_provider=None):
        principals = self.get_principals(headers)

        for action, principal, permission in self.get_complete_acl(
            context_acl_provider
        ):
            if (permission != requested_permission or
                    principal not in principals):
                continue

            if action is Allow:
                return True
            elif action is Deny:
                return False
            else:
                raise ValueError("Invalid action in ACL")

        return False

    def validate_permission(self, requested_permission,
                            headers, context_acl_provider=None):
        try:
            allowed = self.check_permission(
                requested_permission, headers, context_acl_provider)
        except ValueError as e:
            log.exception(e)
            allowed = False

        if allowed:
            return

        raise HTTPException(status_code=403, detail="Permission denied.")


def parse_authorization_header(authorization: str):
    try:
        auth_method, encoded_string = authorization.split(' ')
    except (AttributeError, ValueError):
        raise AuthorizationHeaderNotFound

    if not auth_method == 'Basic':
        raise InvalidAuthorizationMethod('Basic')
    decoded_header = base64.b64decode(encoded_string).decode('utf-8')
    try:
        agent_id, secret = decoded_header.split(':')
    except ValueError:
        raise InvalidAuthorizationHeader(
            "<Method> base64(<agent_id>:<secret>)"
        )
    return {
        'agent_id': agent_id,
        'secret': secret
    }


def create_session_cookie(user):
    return (
        'session',
        jwt.encode(
            {'authenticated_user_id': str(user.id)},
            settings['session']['secret'],
            algorithm='HS256'
        ).decode('utf-8')
    )
