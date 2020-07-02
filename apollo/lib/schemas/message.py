import uuid
from enum import Enum

from pydantic import BaseModel


class Command(Enum):
    NEW_CONNECTION = "new connection"


class BaseMessageSchema(BaseModel):
    connection_id: uuid.UUID


class ShellIOSchema(BaseMessageSchema):
    message: str


class CommandSchema(BaseMessageSchema):
    command: Command
