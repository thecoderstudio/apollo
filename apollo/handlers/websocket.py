from fastapi import WebSocket, Depends
from sqlalchemy.orm import Session

from apollo.lib.router import SecureRouter
from apollo.lib.security import (
    Allow, Agent, get_client_id_from_authorization_header)
from apollo.lib.websocket.agent import AgentConnectionManager
from apollo.models import get_session

router = SecureRouter([(Allow, Agent, 'connect')])


@router.websocket('/ws', permission='connect')
async def connect(
    websocket: WebSocket,
    session: Session = Depends(get_session)
):
    agent_id = get_client_id_from_authorization_header(
        session=session, authorization=websocket.headers['authorization'])
    await AgentConnectionManager().connect(agent_id, websocket)
