import uuid
from enum import Enum

from pydantic import BaseModel


class Command(Enum):
    NEW_CONNECTION = "new connection"
    LINPEAS = "linpeas"


class ServerCommand(Enum):
    FINISHED = "finished"


class BaseMessageSchema(BaseModel):
    connection_id: uuid.UUID


class ShellIOSchema(BaseMessageSchema):
    message: str


class CommandSchema(BaseMessageSchema):
    command: Command


class ServerCommandSchema(BaseMessageSchema):
    command: ServerCommand
