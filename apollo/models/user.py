import uuid

from sqlalchemy import Column, String

from apollo.lib.types.uuid import UUID
from apollo.models import Base, get_session


class User(Base):
    __tablename__ = 'user'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    username = Column(String(36), nullable=False)
    password_hash = Column(String(119), nullable=False)
    password_salt = Column(String(29), nullable=False)


def get_user_by_username(username: str):
    return list(get_session())[0].query(User).filter(User.username == username).one()


def get_user_by_id(id: uuid.UUID):
    return list(get_session())[0].query(User).filter(User.id == id).one()
