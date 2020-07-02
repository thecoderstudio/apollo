import os
import subprocess
import uuid
from typing import List

from fastapi import Depends, WebSocket
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from apollo.lib.router import SecureRouter
from apollo.lib.schemas.agent import (
    AgentSchema, BaseAgentSchema, CreateAgentSchema)
from apollo.lib.security import Allow, Authenticated, Everyone
from apollo.lib.websocket.user import UserConnectionManager
from apollo.models import get_session, save
from apollo.models.agent import Agent, list_all_agents
from apollo.models.oauth import OAuthClient

router = SecureRouter([
    (Allow, Authenticated, 'agent.post'),
    (Allow, Authenticated, 'agent.list'),
    (Allow, Everyone, 'agent.download'),
    (Allow, Authenticated, 'agent.shell')
])


@router.post("/agent", status_code=201, response_model=AgentSchema,
             permission='agent.post')
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


@router.get('/agent/download', status_code=200, permission='agent.download')
async def download_agent():
    # Always make sure to get the latest version
    binary_path = f"/tmp/{uuid.uuid4()}"
    subprocess.run(["go", "get", "-d", "-u",
                    "github.com/thecoderstudio/apollo-agent"])

    env = os.environ.copy()
    env["GOOS"] = "darwin"
    env["GOARCH"] = "amd64"
    subprocess.run(["go", "build", "-o", binary_path,
                    "github.com/thecoderstudio/apollo-agent"], env=env)
    return FileResponse(binary_path)


@router.websocket("/agent/{agent_id}/shell", permission='agent.shell')
async def shell(websocket: WebSocket, agent_id: uuid.UUID):
    await UserConnectionManager().connect(websocket, agent_id)
