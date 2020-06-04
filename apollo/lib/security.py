import base64
import logging

from apollo.lib.exceptions import HTTPException
from apollo.lib.exceptions.oauth import (
    AuthorizationHeaderNotFound, InvalidAuthorizationMethod,
    InvalidAuthorizationHeader)

log = logging.getLogger(__name__)

Everyone = 'Everyone'
Allow = 'Allow'
Deny = 'Deny'


class AuthorizationPolicy:
    def __init__(self, acl_provider):
        self.acl_provider = acl_provider

    @staticmethod
    def get_principals():
        return (Everyone,)

    def get_complete_acl(self, context_acl_provider=None):
        acl = self.acl_provider.__acl__()
        if not context_acl_provider:
            return acl

        return context_acl_provider.__acl__() + acl

    def check_permission(self, requested_permission,
                         context_acl_provider=None):
        principals = self.get_principals()

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
                # TODO customer exception
                raise ValueError("Invalid action in ACL")

        return False

    def validate_permission(self, requested_permission,
                            context_acl_provider=None):
        try:
            allowed = self.check_permission(requested_permission,
                                            context_acl_provider)
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
