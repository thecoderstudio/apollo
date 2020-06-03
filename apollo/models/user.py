import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from apollo.models import Base, get_session


class User(Base):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(36), unique=True, nullable=False)
    password_hash = Column(String(119), nullable=False)
    password_salt = Column(String(29), nullable=False)


def get_user_by_username(username: str):
    return list(get_session())[0].query(User).filter(User.username == username).one()


def get_user_by_id(_id: uuid.UUID, session=list(get_session())[0]):
    return session.query(User).get(_id)
