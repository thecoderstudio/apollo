import uuid

from pydantic import validator, constr, BaseModel, root_validator
from typing import Optional

from apollo.lib.decorators import with_db_session
from apollo.lib.exceptions import PydanticValidationError
from apollo.lib.schemas import ORMBase
from apollo.lib.schemas.role import RoleSchema
from apollo.models.user import get_user_by_username


class BaseCreateOrUpdateUserSchema(BaseModel):
    username: constr(min_length=1, max_length=36, strip_whitespace=True)
    password: constr(min_length=8, strip_whitespace=True)

    @validator('username')
    @classmethod
    @with_db_session
    def username_must_be_unique(cls, value, **kwargs):
        if get_user_by_username(kwargs['session'], value):
            raise ValueError("username must be unique")

        return value

    @validator('password', 'username')
    @classmethod
    def no_whitespace(cls, value, field):
        if ' ' in value:
            raise ValueError(f"{field} can't contain whitespaces")

        return value


class UserSchema(ORMBase):
    id: uuid.UUID
    username: str
    has_changed_initial_password: bool
    role: Optional[RoleSchema]


class UpdateUserSchema(BaseCreateOrUpdateUserSchema):
    username: Optional[constr(
        min_length=1, max_length=36, strip_whitespace=True)]
    password: Optional[constr(min_length=8, strip_whitespace=True)]
    password_confirm: Optional[constr(min_length=8, strip_whitespace=True)]
    old_password: Optional[constr(min_length=8, strip_whitespace=True)]

    @validator('password_confirm')
    @classmethod
    def password_must_match(cls, value, values):
        if value != values.get('password'):
            raise ValueError('passwords must match')

        return value

    @validator('old_password', always=True)
    @classmethod
    def old_password_required(cls, value, values):
        if not value and values.get('password'):
            raise ValueError("old password is required when password is given")

        return value

    @validator('password_confirm', pre=True, always=True)
    @classmethod
    def password_confirm_required(cls, value, values):
        if not value and values.get('password'):
            raise ValueError(
                "password confirm is required when password is given")

        return value

    @root_validator
    @classmethod
    def password_cannot_not_match_old_password(cls, values):
        password = values.get('password')
        if password and password == values.get('old_password'):
            raise PydanticValidationError(
                "password cannot match old password",
                ('password'),
                cls
            )

        return values
