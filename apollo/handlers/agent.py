import uuid

from fastapi import Depends, WebSocket
from starlette.websockets import WebSocketDisconnect
from sqlalchemy.orm import Session

from apollo.lib.router import SecureRouter
from apollo.lib.schemas.agent import AgentSchema, CreateAgentSchema
from apollo.lib.security import Allow, Authenticated
from apollo.lib.websocket import WebSocketManager
from apollo.models import get_session, save
from apollo.models.agent import Agent
from apollo.models.oauth import OAuthClient

router = SecureRouter([
    (Allow, Authenticated, 'agent.post')
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


@router.websocket("/agent/{agent_id}/shell", permission='public')
async def shell(websocket: WebSocket, agent_id: uuid.UUID):
    await websocket.accept()
    session_id = uuid.uuid4()

    manager = WebSocketManager()
    manager.sessions[session_id] = websocket
    try:
        while True:
            command = await websocket.receive_text()
            await WebSocketManager().send_message(agent_id, session_id, command)
    except WebSocketDisconnect:
        return
