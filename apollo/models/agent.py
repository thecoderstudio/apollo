import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from apollo.lib.websocket_manager import WebSocketManager
from apollo.models import Base


class Agent(Base):
    __tablename__ = 'agent'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)

    oauth_client = relationship('OAuthClient', uselist=False,
                                cascade="all, delete-orphan")

    @property
    def connection_status(self):
        try:
            return str(
                WebSocketManager().connections[self.id].client_state).split(
                    '.')[1].lower()
        except KeyError:
            return 'disconnected'


def get_agent_by_name(session, name):
    return session.query(Agent).filter(Agent.name == name).one_or_none()


def list_all_agents(session):
    return session.query(Agent).all()
