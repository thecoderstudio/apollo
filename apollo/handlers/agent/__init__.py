import uuid
from typing import List

from fastapi import Depends, WebSocket
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from apollo.lib.agent import AgentBinary, create_agent_binary
from apollo.lib.decorators import notify_websockets
from apollo.lib.exceptions import HTTPException
from apollo.lib.router import SecureRouter
from apollo.lib.schemas.agent import (
    AgentSchema, BaseAgentSchema, CreateAgentSchema)
from apollo.lib.security import Allow, Authenticated, Everyone
from apollo.lib.websocket.app import (
    AppConnectionManager, WebSocketObserverInterestType)
from apollo.lib.websocket.user import UserShellConnectionManager
from apollo.models import get_session, save
from apollo.models.agent import Agent, list_all_agents, get_agent_by_id
from apollo.models.oauth import OAuthClient

router = SecureRouter([
    (Allow, Authenticated, 'agent.post'),
    (Allow, Authenticated, 'agent.list'),
    (Allow, Authenticated, 'agent.get'),
    (Allow, Everyone, 'agent.download'),
    (Allow, Authenticated, 'agent.shell')
])


@router.post("/agent", status_code=201, response_model=AgentSchema,
             permission='agent.post')
@notify_websockets(
    observer_interest_type=WebSocketObserverInterestType.AGENT_LISTING)
def post_agent(agent_data: CreateAgentSchema,
               session: Session = Depends(get_session)):
    _, id_ = save(session, Agent(
        oauth_client=OAuthClient(type='confidential'),
        **dict(agent_data)
    ))
    return get_agent_by_id(session, id_)


@router.get('/agent', status_code=200, response_model=List[BaseAgentSchema],
            permission='agent.list')
def list_agents(session: Session = Depends(get_session)):
    return list_all_agents(session)


@router.websocket('/agent', permission='agent.list')
async def list_agents_via_websocket(websocket: WebSocket):
    await AppConnectionManager().connect(
        websocket, WebSocketObserverInterestType.AGENT_LISTING)


@router.get('/agent/download', status_code=200, permission='agent.download')
async def download_agent(binary: AgentBinary = Depends(create_agent_binary)):
    return FileResponse(binary.path, filename='apollo-agent')


@router.get("/agent/{agent_id}", permission='agent.get',
            response_model=BaseAgentSchema)
def get_agent(agent_id: uuid.UUID, session: Session = Depends(get_session)):
    agent = get_agent_by_id(session, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found.")

    return agent


@router.websocket("/agent/{agent_id}/shell", permission='agent.shell')
async def shell(websocket: WebSocket, agent_id: uuid.UUID):
    await UserShellConnectionManager().connect(websocket, agent_id)
