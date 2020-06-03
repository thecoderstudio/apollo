import base64

from apollo.lib.exceptions.oauth import (
    AuthorizationHeaderNotFound, InvalidAuthorizationMethod,
    InvalidAuthorizationHeader)


def extract_client_authorization(authorization: str):
    try:
        auth_method, encoded_string = authorization.split(' ')
    except (AttributeError, ValueError):
        raise AuthorizationHeaderNotFound

    if not auth_method == 'Basic':
        raise InvalidAuthorizationMethod('Basic')
    decoded_header = base64.b64decode(encoded_string).decode('utf-8')
    try:
        agent_id, client_secret = decoded_header.split(':')
    except ValueError:
        raise InvalidAuthorizationHeader(
            "<Method> base64(<agent_id>:<client_secret>)"
        )
    return {
        'agent_id': agent_id,
        'client_secret': client_secret
    }
