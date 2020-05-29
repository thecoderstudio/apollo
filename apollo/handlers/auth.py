from datetime import timedelta

from fastapi import APIRouter, Depends, security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)

from apollo.lib.exceptions import credentials_exception
from apollo.lib.settings import settings
from apollo.lib.hash import compare_plaintext_to_hash
from apollo.lib.jwt import create_access_token
from apollo.lib.schemas.auth import TokenSchema, RequestTokenSchema
from apollo.models.user import User, get_user_by_username

router = APIRouter()


@router.post('/token', response_model=TokenSchema)
async def get_token(form_data: RequestTokenSchema):
    user = get_user_by_username(form_data.username)
    if not user:
        raise credentials_exception

    password_match = compare_plaintext_to_hash(
        form_data.password, user.password_hash, user.password_salt)
    if not password_match:
        raise credentials_exception
    print(settings['app']['access_token_experation_in_minutes'])
    access_token_expires = timedelta(
        minutes=int(settings['app']['access_token_experation_in_minutes']))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
