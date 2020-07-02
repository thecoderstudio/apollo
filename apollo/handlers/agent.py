import uuid
from typing import List

from fastapi import Depends, WebSocket
from sqlalchemy.orm import Session

from apollo.lib.decorators import notify_websockets
from apollo.lib.router import SecureRouter
from apollo.lib.schemas.agent import (
    AgentSchema, BaseAgentSchema, CreateAgentSchema)
from apollo.lib.security import Allow, Authenticated
from apollo.lib.websocket.app import (
    AppConnectionManager, WebSocketObserverInterestType)
from apollo.lib.websocket.user import UserConnectionManager
from apollo.models import get_session, save
from apollo.models.agent import Agent, list_all_agents
from apollo.models.oauth import OAuthClient

router = SecureRouter([
    (Allow, Authenticated, 'agent.post'),
    (Allow, Authenticated, 'agent.list'),
    (Allow, Authenticated, 'agent.shell')
])


@router.post("/agent", status_code=201, response_model=AgentSchema,
             permission='agent.post')
@notify_websockets(
    observer_interest_type=WebSocketObserverInterestType.AGENT_LISTING)
def post_agent(agent_data: CreateAgentSchema,
               session: Session = Depends(get_session)):
    agent, _ = save(session, Agent(
        oauth_client=OAuthClient(type='confidential'),
        **dict(agent_data)
    ))
    return agent


@router.get('/agent', status_code=200, response_model=List[BaseAgentSchema],
            permission='agent.list')
def list_agents(session: Session = Depends(get_session)):
    return list_all_agents(session)


@router.websocket('/agent', permission='agent.list')
async def list_agents_via_websocket(websocket: WebSocket):
    await AppConnectionManager().connect_and_send(
        websocket, WebSocketObserverInterestType.AGENT_LISTING)


@router.websocket("/agent/{agent_id}/shell", permission='agent.shell')
async def shell(websocket: WebSocket, agent_id: uuid.UUID):
    await UserConnectionManager().connect(websocket, agent_id)
