import uuid
import string

from typing import Optional
from pydantic import Field, Schema, validator, constr
from sqlalchemy.orm.exc import NoResultFound

from apollo.lib.schemas import ORMSchema
from apollo.models.user import get_user_by_username


class UserInSchema(ORMSchema):
    username: str
    password: constr(min_length=8)

    @validator('username')
    def name_must_be_unique(cls, value):
        try:
            get_user_by_username(value)
            raise ValueError('username must be unique')
        except NoResultFound:
            return value
        
    
class UserOutSchema(ORMSchema):
    id: uuid.UUID
    username: str