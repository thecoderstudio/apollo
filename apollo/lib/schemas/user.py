import uuid
import string

from pydantic import BaseModel, Field

class User(BaseModel):
    id: uuid.UUID
    password:  Field(min_length=8)
