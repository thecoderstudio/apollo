import uuid

from sqlalchemy import Column, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from apollo.models import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(36), unique=True, nullable=False)
    password_hash = Column(String(119), nullable=False)
    password_salt = Column(String(29), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('role.id'))
    has_changed_initial_password = Column(Boolean, default=False)
    role = relationship('Role')

    def set_fields(self, data=None):
        for key, value in data.items():
            setattr(self, key, value)


def get_user_by_id(session, id_):
    return session.query(User).get(id_)


def get_user_by_username(session, username: str):
    return session.query(User).filter(User.username == username).one_or_none()


def count_users(session):
    return session.query(User).count()


def list_users(session):
    return session.query(User).all()
