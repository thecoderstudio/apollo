from pydantic import BaseModel

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class RequestTokenSchema(BaseModel):
    username: str
    password: str

