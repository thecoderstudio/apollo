import base64
import copy

import jwt
from sqlalchemy.orm.exc import NoResultFound

from apollo.lib.decorators import with_db_session
from apollo.lib.exceptions import HTTPException
from apollo.lib.exceptions.oauth import (
    AuthorizationHeaderNotFound, InvalidAuthorizationMethod,
    InvalidAuthorizationHeader)
from apollo.lib.logging import audit_logger as log
from apollo.lib.settings import settings
from apollo.models.oauth import get_access_token_by_token
from apollo.models.user import get_user_by_id

Admin = 'role:admin'
Authenticated = 'Authenticated'
Allow = 'Allow'
Agent = 'Agent'
Deny = 'Deny'
Everyone = 'Everyone'
Human = 'Human'

JWT_ALGORITHM = 'HS256'


class AuthorizationPolicy:
    def __init__(self, acl_provider):
        self.acl_provider = acl_provider

    def enhance_http_connection(self, http_connection, session):
        enhanced_http_connection = copy.copy(http_connection)
        enhanced_http_connection.oauth_client = None
        enhanced_http_connection.current_user = self._get_current_user(
            enhanced_http_connection.cookies, session)

        access_token = self._get_authenticated_access_token(
            enhanced_http_connection.headers, session)
        if access_token:
            enhanced_http_connection.oauth_client = access_token.client

        return enhanced_http_connection

    @staticmethod
    @with_db_session
    def get_principals(enhanced_http_connection, session):
        principals = [Everyone]

        if enhanced_http_connection.oauth_client:
            principals += [
                Authenticated,
                Agent,
                f"agent:{enhanced_http_connection.oauth_client.agent_id}"
            ]

        authenticated_user = enhanced_http_connection.current_user
        if authenticated_user:
            principals += [Authenticated, Human,
                           f"user:{authenticated_user.id}"]
            if authenticated_user.role:
                principals.append(f"role:{authenticated_user.role.name}")

        log.debug(f"Found principals: {principals}")

        return principals

    @staticmethod
    def _get_authenticated_access_token(headers, session):
        try:
            auth_method, token_string = get_auth_method_and_token(
                headers['authorization'])
        except KeyError:
            return

        if auth_method != 'Bearer':
            return

        try:
            access_token = get_access_token_by_token(session, token_string)
        except NoResultFound:
            return
        if not access_token.client.active or access_token.expired:
            return

        log.info(
            f"Authenticated access token for agent: {access_token.client_id}"
        )
        return access_token

    @staticmethod
    def _get_current_user(cookies, session):
        try:
            payload = jwt.decode(
                cookies['session'],
                settings['session']['secret'],
                algorithms=[JWT_ALGORITHM]
            )
        except KeyError:
            return None

        auth_user_id = payload['authenticated_user_id']
        log.info(f"Authenticated user: {auth_user_id}")

        return get_user_by_id(session, auth_user_id)

    def get_complete_acl(self, context_acl_provider=None):
        acl = self.acl_provider.__acl__()
        if not context_acl_provider:
            return acl

        complete_acl = context_acl_provider.__acl__() + acl
        log.debug(f"complete ACL: {complete_acl}")

        return complete_acl

    def check_permission(self, requested_permission,
                         enhanced_http_connection, context_acl_provider=None):
        principals = self.get_principals(enhanced_http_connection)

        for action, principal, permission in self.get_complete_acl(
            context_acl_provider
        ):
            if (permission != requested_permission or
                    principal not in principals):
                continue

            if action is Allow:
                log.info(f"Permission '{permission}' granted")
                return True
            elif action is Deny:
                log.info(f"Permission '{permission}' denied")
                return False
            else:
                raise ValueError("Invalid action in ACL")

        return False

    def validate_permission(self, requested_permission,
                            enhanced_http_connection,
                            context_acl_provider=None):
        try:
            allowed = self.check_permission(
                requested_permission, enhanced_http_connection,
                context_acl_provider)
        except ValueError as e:
            log.exception(e)
            allowed = False

        if allowed:
            return

        raise HTTPException(status_code=403, detail="Permission denied.")


def parse_authorization_header(authorization: str):
    invalid_header_exception = InvalidAuthorizationHeader(
        "<Method> base64(<agent_id>:<secret>)"
    )

    try:
        auth_method, encoded_string = authorization.split(' ')
    except AttributeError:
        raise AuthorizationHeaderNotFound
    except ValueError:
        raise invalid_header_exception

    if not auth_method == 'Basic':
        raise InvalidAuthorizationMethod('Basic')

    decoded_header = base64.b64decode(encoded_string).decode('utf-8')

    try:
        agent_id, secret = decoded_header.split(':')
    except ValueError:
        raise invalid_header_exception

    log.info(
        f"Verified OAuth client credentials for agent: {agent_id}"
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
            algorithm=JWT_ALGORITHM
        ).decode('utf-8')
    )


def get_auth_method_and_token(authorization: str):
    try:
        auth_method, token_string = authorization.split(' ')
        return auth_method, token_string
    except (AttributeError, ValueError):
        return None, None


def get_client_id_from_authorization_header(session, authorization):
    _, token = get_auth_method_and_token(authorization)
    try:
        return get_access_token_by_token(session, token).client_id
    except NoResultFound:
        return
