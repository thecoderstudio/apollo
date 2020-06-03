from enum import Enum

from pydantic import BaseModel

from apollo.lib.schemas import ORMBase


class GrantType(str, Enum):
    client_credentials = 'client_credentials'


class OAuthAccessTokenSchema(ORMBase):
    access_token: str
    expires_in: int
    token_type: str


class CreateOAuthAccessTokenSchema(BaseModel):
    grant_type: GrantType
