import uuid 

from sqlalchemy import Column, String

from apollo.lib.types.uuid import UUID
from apollo.models import Base

class User(Base):
    __tablename__ = 'user'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    password_hash = Column(String(119), nullable=False)
    password_salt = Column(String(29), nullable=False)