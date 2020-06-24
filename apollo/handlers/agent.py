from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from apollo.lib.router import SecureRouter
from apollo.lib.schemas.agent import AgentSchema, CreateAgentSchema
from apollo.lib.security import Allow, Authenticated
from apollo.models import get_session, save
from apollo.models.agent import Agent, list_all_agents
from apollo.models.oauth import OAuthClient

router = SecureRouter([(Allow, Authenticated, 'agent.post'),
                       (Allow, Authenticated, 'agent.list')])


@router.post("/agent", status_code=201, response_model=AgentSchema,
             permission='agent.post')
def post_agent(agent_data: CreateAgentSchema,
               session: Session = Depends(get_session)):
    agent, _ = save(session, Agent(
        oauth_client=OAuthClient(type='confidential'),
        **dict(agent_data)
    ))
    return agent


@router.get('/agent', status_code=200, response_model=List[AgentSchema],
            permission='agent.list')
def list_agents(session: Session = Depends(get_session)):
    return list_all_agents(session)[0]
