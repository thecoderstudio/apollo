import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from apollo.models import Base


class Role(Base):
    __tablename__ = 'role'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)


def get_role_by_name(session, name):
    return session.query(Role).filter(Role.name == name).one()
