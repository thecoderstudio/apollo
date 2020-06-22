import uuid

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from apollo.lib.router import SecureRouter
from apollo.lib.schemas.agent import AgentSchema, CreateAgentSchema
from apollo.lib.security import Allow, Authenticated
from apollo.lib.websocket_manager import WebSocketManager
from apollo.models import get_session, save
from apollo.models.agent import Agent
from apollo.models.oauth import OAuthClient

router = SecureRouter([(Allow, Authenticated, 'agent.post'),
                       (Allow, Authenticated, 'websocket.close')])


@router.post("/agent", status_code=201, response_model=AgentSchema,
             permission='agent.post')
def post_agent(agent_data: CreateAgentSchema,
               session: Session = Depends(get_session)):
    agent, _ = save(session, Agent(
        oauth_client=OAuthClient(type='confidential'),
        **dict(agent_data)
    ))
    return agent


@router.get('/agent/{agent_id}/close', permission='public')
async def close_websocket_connection(agent_id: uuid.UUID):
    pass
    try:
        await WebSocketManager().close_and_remove_connection(agent_id)
    except KeyError:
        raise HTTPException(status_code=404)
