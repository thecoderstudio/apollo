from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apollo.lib.schemas.agent import AgentSchema, CreateAgentSchema
from apollo.models import get_session, save
from apollo.models.agent import Agent
from apollo.models.oauth import OAuthClient

router = APIRouter()


@router.post("/agent", status_code=201, response_model=AgentSchema)
def post_agent(agent_data: CreateAgentSchema,
               session: Session = Depends(get_session)):
    agent, _ = save(session, Agent(
        oauth_client=OAuthClient(client_type='confidential'),
        **dict(agent_data)
    ))
    return agent
