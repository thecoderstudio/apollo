from datetime import timedelta, datetime

import jwt

from apollo.lib.settings import settings


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    encoded_jwt = jwt.encode(
        to_encode, settings['app']['access_token_key'], algorithm="HS256")
    return encoded_jwt
