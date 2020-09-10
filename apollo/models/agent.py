import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from starlette.websockets import WebSocketState

from apollo.lib.websocket.agent import AgentConnectionManager
from apollo.models import Base


class Agent(Base):
    __tablename__ = 'agent'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    #external_ip_address = Column(String(16), nullable=True)
    #operating_system = Column(String(100), nullable=True)

    oauth_client = relationship('OAuthClient', uselist=False,
                                cascade="all, delete-orphan")

    @property
    def connection_state(self):
        try:
            return AgentConnectionManager().get_connection(
                self.id
            ).client_state
        except KeyError:
            return WebSocketState.DISCONNECTED


def get_agent_by_name(session, name):
    return session.query(Agent).filter(Agent.name == name).one_or_none()


def get_agent_by_id(session, id_):
    return session.query(Agent).get(id_)


def list_all_agents(session):
    return session.query(Agent).all()
