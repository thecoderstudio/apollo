import uuid

from fastapi import Depends, WebSocket
from sqlalchemy.orm import Session

from apollo.models import get_session
from apollo.lib.websocket_manager import WebSocketManager
from apollo.lib.security import (
    Agent, Allow, Authenticated, get_client_id_from_authorization_header)
from apollo.lib.router import SecureRouter


router = SecureRouter([(Allow, Agent, 'shell')])


@router.websocket('/ws', permission='shell')
async def shell(
    websocket: WebSocket,
    session: Session = Depends(get_session)
):
    client_id = get_client_id_from_authorization_header(
        session=session, authorization=websocket.headers['authorization'])
    await WebSocketManager().add_and_connect_websocket(
        client_id=client_id, websocket=websocket)
