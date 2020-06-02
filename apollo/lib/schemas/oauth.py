from enum import Enum

from pydantic import BaseModel


class GrantType(str, Enum):
    client_credentials = 'client_credentials'


class OAuthAccessTokenSchema(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    grant_type: GrantType
