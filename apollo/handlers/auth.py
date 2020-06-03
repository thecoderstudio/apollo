from datetime import timedelta

from fastapi import APIRouter

from apollo.lib.exceptions import invalid_credentials_exception
from apollo.lib.settings import settings
from apollo.lib.encrypt import compare_plaintext_to_hash, create_access_token
from apollo.lib.schemas.auth import TokenSchema, RequestTokenSchema
from apollo.models.user import get_user_by_username

router = APIRouter()


@router.post('/token', response_model=TokenSchema)
def get_token(form_data: RequestTokenSchema):
    user = get_user_by_username(form_data.username)
    if not user:
        raise invalid_credentials_exception

    password_match = compare_plaintext_to_hash(
        form_data.password, user.password_hash, user.password_salt)
    if not password_match:
        raise invalid_credentials_exception

    access_token_expires = timedelta(
        minutes=int(settings['app']['access_token_experation_in_minutes']))
    access_token = create_access_token(
        data={"user_id": str(user.id)}, expires_in=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
