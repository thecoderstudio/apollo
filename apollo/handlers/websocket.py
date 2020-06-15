from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import WebSocket, Depends

from apollo.lib.router import SecureRouter
from apollo.lib.security import (
    Allow, Agent, get_client_id_from_authorization_header)
from apollo.lib.websocket_manager import WebSocketManager
from apollo.models import get_session

router = SecureRouter([(Allow, Agent, 'shell')])


@router.websocket('/ws', permission='shell')
async def shell(
    websocket: WebSocket,
    session: Session = Depends(get_session)
):
    client_id = get_client_id_from_authorization_header(
        session, websocket.headers['authorization'])
    await WebSocketManager().add_and_connect_websocket(
        client_id, websocket)


router2 = APIRouter()


@ router2.post('/message')
async def messagge():
    print(WebSocketManager().connections)
    import uuid
    await WebSocketManager().send_message(uuid.UUID('2d022ebd-bfc2-4906-8c9e-4e065fab9435'),
                                          'ls')
