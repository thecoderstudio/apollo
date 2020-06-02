from pydantic import BaseModel


class CreateAgentSchema(BaseModel):
    name: str
