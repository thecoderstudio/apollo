from fastapi import WebSocket

from apollo.lib.router import SecureRouter
from apollo.lib.security import Allow, Agent

router = SecureRouter([(Allow, Agent, 'shell')])


@router.websocket_('/ws', permission='shell')
async def shell(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json("Connection accepted")
