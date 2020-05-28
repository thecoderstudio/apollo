import uuid
import string

from pydantic import BaseModel, Field

class UserSchema(BaseModel):
    id: uuid.UUID
    password:  Field(min_length=8)
