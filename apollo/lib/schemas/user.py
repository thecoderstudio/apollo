import uuid
import string

from typing import Optional
from pydantic import Field, Schema

from apollo.lib.schemas import ORMSchema

class UserSchema(ORMSchema):
    id: Optional[uuid.UUID]
    username: str
    password: Optional[str]
