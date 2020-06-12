from fastapi import WebSocket, APIRouter

from apollo.lib.router import SecureRouter
from apollo.lib.security import Allow, Agent
from apollo.lib.websocket_manager import WebSocketManager

router = SecureRouter([(Allow, Agent, 'shell')])


@router.websocket('/ws', permission='shell')
async def shell(websocket: WebSocket):
    await WebSocketManager().add_and_connect_websocket(websocket)
