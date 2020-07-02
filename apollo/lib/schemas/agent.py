import uuid

from pydantic import BaseModel, constr, validator
from starlette.websockets import WebSocketState

from apollo.lib.agent import SupportedArch, SupportedOS
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


class BaseAgentSchema(ORMBase):
    id: uuid.UUID
    name: str
    connection_state: WebSocketState

    @validator('connection_state')
    @classmethod
    def parse_to_string(cls, v):
        return v.name.lower()


class AgentSchema(BaseAgentSchema):
    oauth_client: OAuthClientSchema


class AgentBinarySchema(BaseModel):
    target_os: SupportedOS
    target_arch: SupportedArch
