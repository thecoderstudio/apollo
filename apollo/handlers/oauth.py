import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from apollo.lib.exceptions.oauth import (
    AuthorizationHeaderNotFound, InvalidAuthorizationMethod,
    InvalidAuthorizationHeader)
from apollo.lib.schemas.oauth import (
    CreateOAuthAccessTokenSchema, OAuthAccessTokenSchema)
from apollo.lib.security import extract_client_authorization
from apollo.models import get_session, save
from apollo.models.oauth import get_client_by_creds, OAuthAccessToken

router = APIRouter()


@router.post('/oauth/token', status_code=201,
             response_model=OAuthAccessTokenSchema)
def post_access_token(
    token_data: CreateOAuthAccessTokenSchema,
    session: Session = Depends(get_session),
    authorization: str = Header(None)
):
    client = get_client(session, authorization)
    if (token_data.grant_type == 'client_credentials' and
            client.client_type != 'confidential'):
        raise HTTPException(
            status_code=400,
            detail="Client not authorized to use this grant type"
        )

    token = OAuthAccessToken(
        client=client,
        expiry_date=(datetime.datetime.now(datetime.timezone.utc) +
                     datetime.timedelta(hours=1))
    )

    save(session, token)
    return token


def get_client(session: Session, authorization: str):
    try:
        credentials = extract_client_authorization(authorization)
        return get_client_by_creds(session, **credentials)
    except NoResultFound:
        raise HTTPException(status_code=400,
                            detail="No client found for given client_id")
    except (AuthorizationHeaderNotFound, InvalidAuthorizationMethod,
            InvalidAuthorizationHeader) as e:
        raise HTTPException(status_code=400, detail=e.message)
