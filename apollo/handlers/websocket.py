import uuid

from fastapi import Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session

from apollo.models import get_session
from apollo.lib.websocket_manager import WebSocketManager
from apollo.lib.security import (
    Agent, Allow, get_client_id_from_authorization_header)
from apollo.lib.router import SecureRouter


router = SecureRouter([
    (Allow, Agent, 'shell'),
    (Allow, 'role:admin', 'websocket.close')
])


@router.websocket('/ws', permission='shell')
async def shell(
    websocket: WebSocket,
    session: Session = Depends(get_session)
):
    client_id = get_client_id_from_authorization_header(
        session=session, authorization=websocket.headers['authorization'])
    await WebSocketManager().add_and_connect_websocket(
        client_id=client_id, websocket=websocket)


@router.get('/ws/{websocket_id}/close', permission='websocket.close')
async def close_websocket_connection(websocket_id: uuid.UUID):
    try:
        await WebSocketManager().close_and_remove_connection(websocket_id)
    except KeyError:
        raise HTTPException(status_code=404)
