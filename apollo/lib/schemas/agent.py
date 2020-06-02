from pydantic import BaseModel, constr, validator

from apollo.lib.decorators import with_db_session
from apollo.models.agent import get_agent_by_name


class CreateAgentSchema(BaseModel):
    name: constr(min_length=1, max_length=100, strip_whitespace=True)

    @validator('name')
    @with_db_session
    def name_must_not_exist(cls, name, **kwargs):
        session = kwargs['session']
        if not get_agent_by_name(session, name):
            return

        raise ValueError("An agent with the given name already exists")
