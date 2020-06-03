import datetime
import logging
import uuid
from secrets import token_hex

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from apollo.models import Base

log = logging.getLogger(__name__)


class OAuthClient(Base):
    __tablename__ = 'oauth_client'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agent.id'),
                      unique=True, nullable=False)
    client_secret = Column(String(64), nullable=False,
                           default=lambda: token_hex(32))
    client_type = Column(Enum("confidential", name="client_type"),
                         nullable=False)
    active = Column(Boolean, default=True, nullable=False)


class OAuthAccessToken(Base):
    __tablename__ = 'oauth_access_token'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('oauth_client.id'),
                       nullable=False)
    access_token = Column(String(64), unique=True, nullable=False,
                          default=lambda: token_hex(32))
    token_type = Column(Enum("Bearer", name="token_type"), default="Bearer",
                        nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)

    client = relationship('OAuthClient')

    @property
    def expires_in(self):
        seconds_left = (self.expiry_date - datetime.datetime.now(
            datetime.timezone.utc)
        ).total_seconds()
        return seconds_left if seconds_left > 0 else 0

    @property
    def expired(self):
        return self.expires_in == 0


def get_client_by_creds(session, agent_id, client_secret):
    return session.query(OAuthClient).filter(
        OAuthClient.agent_id == agent_id,
        OAuthClient.client_secret == client_secret).one()
