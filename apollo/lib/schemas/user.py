import uuid

from pydantic import validator, constr, BaseModel
from typing import Optional

from apollo.lib.decorators import with_db_session
from apollo.lib.schemas import ORMBase
from apollo.lib.schemas.role import RoleSchema
from apollo.models.user import get_user_by_username


def check_for_whitespace(value):
    if ' ' in value:
        raise ValueError("password can't contain whitespaces")

    return value


class CreateUserSchema(BaseModel):
    username: constr(min_length=1, max_length=36, strip_whitespace=True)
    password: constr(min_length=8, strip_whitespace=True)

    @validator('username')
    @classmethod
    @with_db_session
    def username_must_be_unique(cls, value, **kwargs):
        if get_user_by_username(kwargs['session'], value):
            raise ValueError("username must be unique")

        return value

    @validator('password')
    @classmethod
    def no_whitespace_in_password(cls, value):
        return check_for_whitespace(value)


class UserSchema(ORMBase):
    id: uuid.UUID
    username: str
    has_changed_initial_password: bool
    role: Optional[RoleSchema]


class UpdateUserSchema(BaseModel):
    old_password: constr(min_length=8, strip_whitespace=True)
    password: constr(min_length=8, strip_whitespace=True)
    password_confirm: constr(min_length=8, strip_whitespace=True)

    @validator('password')
    @classmethod
    def no_whitespace_in_password(cls, value):
        return check_for_whitespace(value)

    @validator('password_confirm')
    @classmethod
    def password_must_match(cls, v, values):
        if v != values.get('password'):
            raise ValueError('passwords must match')

        return v

    @validator('password')
    @classmethod
    def password_cannot_not_match_old_password(cls, v, values):
        if v == values['old_password']:
            raise ValueError('password cannot match old password')

        return v
