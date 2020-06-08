import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from apollo.models import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(36), unique=True, nullable=False)
    password_hash = Column(String(119), nullable=False)
    password_salt = Column(String(29), nullable=False)


def get_user_by_id(session, id_):
    return session.query(User).get(id_)


def get_user_by_username(session, username: str):
    return session.query(User).filter(User.username == username).one_or_none()


def count_users(session):
    return session.query(User).count()
