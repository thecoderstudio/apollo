import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from apollo.models import Base


class Agent(Base):
    __tablename__ = 'agent'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)

    oauth_client = relationship('OAuthClient', uselist=False)


def get_agent_by_name(session, name):
    return session.query(Agent).filter(Agent.name == name).one_or_none()
