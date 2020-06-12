import uuid
from fastapi import WebSocket, HTTPException

from apollo.lib.router import SecureRouter
from apollo.lib.security import Allow, Agent
from apollo.lib.websocket_manager import WebSocketManager

router = SecureRouter([(Allow, Agent, 'shell')])


@router.websocket('/ws', permission='public')
async def shell(websocket: WebSocket):
    await WebSocketManager().add_and_connect_websocket(websocket)


@router.post('/ws/{websocket_id}')
async def close_websocket_connection(websocket_id: uuid.UUID):
    try:
        await WebSocketManager().close_and_remove_connection(websocket_id)
    except KeyError:
        raise HTTPException(status_code=404)

