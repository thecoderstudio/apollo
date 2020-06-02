import base64
import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from apollo.lib.exceptions.oauth import (
    AuthorizationHeaderNotFound, InvalidAuthorizationMethod,
    InvalidAuthorizationHeader)
from apollo.lib.schemas.oauth import OAuthAccessTokenSchema
from apollo.models import get_session, save
from apollo.models.oauth import get_client, OAuthAccessToken

router = APIRouter()


@router.post('/oauth/token', status_code=201,
             response_model=OAuthAccessTokenSchema)
def post_access_token(
    session: Session = Depends(get_session),
    authorization: str = Header(None)
):
    try:
        credentials = extract_client_authorization(authorization)
        client = get_client(session, **credentials)
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail="No client found for given client_id")
    except (AuthorizationHeaderNotFound, InvalidAuthorizationMethod,
            InvalidAuthorizationHeader) as e:
        raise HTTPException(status_code=400, detail=e.message)

    # TODO validate client
    token = OAuthAccessToken(
        client=client,
        expiry_date=(datetime.datetime.now(datetime.timezone.utc) +
                     datetime.timedelta(hours=1))
    )

    save(session, token)
    return token


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
