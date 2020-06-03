import uuid

from pydantic import validator, constr, BaseModel
from sqlalchemy.orm.exc import NoResultFound

from apollo.lib.decorators import with_db_session
from apollo.lib.schemas import ORMBase
from apollo.models.user import get_user_by_username


class UserInSchema(BaseModel):
    username: str
    password: constr(min_length=8)

    @validator('username')
    @classmethod
    @with_db_session
    def name_must_be_unique(cls, value, **kwargs):
        try:
            get_user_by_username(kwargs['session'], value)
            raise ValueError('username must be unique')
        except NoResultFound:
            return value


class UserOutSchema(ORMBase):
    id: uuid.UUID
    username: str
