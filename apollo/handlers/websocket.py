import logging
import uuid

from fastapi import WebSocket, Depends
from sqlalchemy.orm import Session

from apollo.lib.router import SecureRouter
from apollo.lib.security import (
    Allow, Agent, get_client_id_from_authorization_header)
from apollo.lib.websocket.agent import AgentConnectionManager
from apollo.models import get_session, save
from apollo.models.agent import get_agent_by_id

router = SecureRouter([(Allow, Agent, 'connect')])


@router.websocket('/ws', permission='connect')
async def connect(
    websocket: WebSocket,
    session: Session = Depends(get_session)
):
    agent_id = get_client_id_from_authorization_header(
        session=session, authorization=websocket.headers['authorization'])
    update_agent_machine_info(websocket, session, agent_id)
    await AgentConnectionManager().connect(agent_id, websocket)

def update_agent_machine_info(
    websocket: WebSocket,
    session: Session,
    agent_id: uuid.UUID
):
    agent = get_agent_by_id(session, agent_id)
    agent.external_ip_address = websocket.client.host
    # save(session, agent)
