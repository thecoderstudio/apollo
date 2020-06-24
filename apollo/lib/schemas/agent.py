import uuid
from enum import Enum

from pydantic import BaseModel, constr, validator

from apollo.lib.decorators import with_db_session
from apollo.lib.schemas import ORMBase
from apollo.lib.schemas.oauth import OAuthClientSchema
from apollo.models.agent import get_agent_by_name


class CreateAgentSchema(BaseModel):
    name: constr(min_length=1, max_length=100, strip_whitespace=True)

    @validator('name')
    @classmethod
    @with_db_session
    def name_must_not_exist(cls, name, **kwargs):
        session = kwargs['session']
        if not get_agent_by_name(session, name):
            return name

        raise ValueError("An agent with the given name already exists")


class ConnectionStateEnum(str, Enum):
    connecting = 'connecting'
    connected = 'connected'
    disconnected = 'disconnected'
    no_connection_available = 'no connection available'


class AgentSchema(ORMBase):
    id: uuid.UUID
    name: str
    oauth_client: OAuthClientSchema
    connection_status: ConnectionStateEnum
