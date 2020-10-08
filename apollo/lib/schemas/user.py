import uuid

from pydantic import (validator, constr, BaseModel, root_validator,
                      ValidationError)
from pydantic.errors import PydanticValueError
from pydantic.error_wrappers import ErrorWrapper

from typing import Optional

from apollo.lib.decorators import with_db_session
from apollo.lib.schemas import ORMBase
from apollo.lib.schemas.role import RoleSchema
from apollo.models.user import get_user_by_username


class CustomPydanticError(PydanticValueError):
    msg_template = 'field required'


def check_for_whitespace(value):
    if ' ' in value:
        raise ValueError("field can't contain whitespaces")

    return value


def check_for_unique_username(value, session):
    if get_user_by_username(session, value):
        raise ValueError("username must be unique")

    return value


class CreateUserSchema(BaseModel):
    username: constr(min_length=1, max_length=36, strip_whitespace=True)
    password: constr(min_length=8, strip_whitespace=True)

    @validator('username')
    @classmethod
    @with_db_session
    def username_must_be_unique(cls, value, **kwargs):
        return check_for_unique_username(value, kwargs['session'])

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
    username: Optional[
        constr(min_length=1, max_length=36, strip_whitespace=True)]
    password: Optional[constr(min_length=8, strip_whitespace=True)]
    password_confirm: Optional[constr(min_length=8, strip_whitespace=True)]
    old_password: Optional[constr(min_length=8, strip_whitespace=True)]

    class Config:
        arbitrary_types_allowed = True

    # @validator('username')
    # @classmethod
    # @with_db_session
    # def unique_username(cls, value, **kwargs):
    #     return check_for_unique_username(value, kwargs['session'])

    # @validator('password', 'username')
    # @classmethod
    # def no_whitespace(cls, value, values):
    #     return check_for_whitespace(value)

    # @validator('password_confirm')
    # @classmethod
    # def password_must_match(cls, v, values):
    #     if v != values.get('password'):
    #         raise ValueError('passwords must match')

    #     return v

    # @validator('old_password', always=True)
    # @classmethod
    # def old_password_required(cls, v, values):
    #     print(values)
    #     if not v and values.get('password'):
    #         raise ValueError("old password is required when password is given")

    #     return v

    # @validator('password_confirm', pre=True, always=True)
    # @classmethod
    # def password_confirm_required(cls, v, values):
    #     if not v and values.get('password'):
    #         raise ValueError(
    #             "password confirm is required when password is given")

    #     return v

    @root_validator
    def password_cannot_not_match_old_password(cls, values):
        password = values.get('password')
        if password:
            print("&****")
            # if password == values.get('old_password'):

            known_field = cls.__fields__.get('old_password', None)
            value, error_ = known_field.validate(
                'aaa', values, loc='old_password', cls=cls)

            print(type(error_))
            raise ValidationError(
                [ErrorWrapper(CustomPydanticError(), ('old_password'))], cls)
            # print(values)
            # known_field = cls.__pydantic_model__.__fields__.get(
            #     'old_password', None)
            print(")(*&(*&")
            # print(known_field)
        # raise ValidationError
        # raise ValueError("password cannot match old password")
