import datetime
import logging
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from apollo.models import Base
from apollo.lib.crypto import get_random_token

log = logging.getLogger(__name__)


class OAuthClient(Base):
    __tablename__ = 'oauth_client'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True,
                      nullable=False)
    client_secret = Column(String(64), default=lambda: get_random_token(32),
                           nullable=False)
    client_type = Column(Enum("confidential", name="client_type"),
                         nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    def set_fields(self, data):
        for key, value in data.items():
            setattr(self, key, value)


class OAuthAccessToken(Base):
    __tablename__ = 'oauth_access_token'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('oauth_client.id'),
                       nullable=False)
    access_token = Column(String(64), default=lambda: get_random_token(32),
                          unique=True, nullable=False)
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
