import uuid 

from sqlalchemy import Column, String

from apollo.lib.types.uuid import UUID
from apollo.models import Base, get_session

class User(Base):
    __tablename__ = 'user'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    password_hash = Column(String(119), nullable=False)
    password_salt = Column(String(29), nullable=False)

def list_users():
    return list(get_session())[0].query(User)
